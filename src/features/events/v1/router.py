from datetime import datetime, timedelta
from typing import Annotated, cast

import pendulum
from fastapi import (
    APIRouter,
    BackgroundTasks,
    Body,
    Depends,
    HTTPException,
    Path,
    Request,
    status,
)

from src.common.exceptions import (
    BadRequestException,
    NotFoundException,
    UnauthorisedException,
)
from src.common.utils.responses import CustomResponse, build_response
from src.core.auth.bearer import JWTBearer
from src.features.auth.models import UserModel
from src.features.companies.dependencies import CompaniesRepoDep, StaffRepoDep
from src.features.companies.models import CompanyModel, StaffModel, StaffRole
from src.features.events.models import (
    EventAttendeeModel,
    EventModel,
    EventStatus,
    EventTableModel,
    EventTicketModel,
)
from src.features.events.schemas import (
    EventAttendeeCreateSchema,
    EventAttendeeSchema,
    EventCreateSchema,
    EventDetailsSchema,
    EventSchema,
    EventTableSchema,
)
from src.features.events.utils.ticket import (
    notify_user_of_ticket_scan,
    send_event_ticket,
)

from ..dependencies import (
    AttendeesRepoDep,
    EventsRepoDep,
    EventTablesRepoDep,
    TicketsRepoDep,
)

router = APIRouter(
    prefix="/events", dependencies=[Depends(JWTBearer())], tags=["Events"]
)


@router.post("/", name="event-create", response_model=CustomResponse[EventSchema])
def create_event(
    request: Request,
    event_data: EventCreateSchema,
    repo: EventsRepoDep,
    staff_repo: StaffRepoDep,
    company_repo: CompaniesRepoDep,
):
    """
    Create a company event
    """
    user: UserModel = request.user

    company_id = event_data.company_id
    db_company = cast(CompanyModel, company_repo.get_by_id(company_id))
    if db_company is None:
        raise NotFoundException("This company does not exists")

    # TODO: Extract this into a dependency
    staff = staff_repo.get_by_column(StaffModel.user_id == user.id)
    if staff:
        if not (
            staff.has_role(StaffRole.creator)
            and cast(int, staff.company_id) == company_id
        ):
            raise UnauthorisedException()
    else:
        # Check if user is owner
        if cast(int, db_company.owner_id) != user.id:
            raise UnauthorisedException()

    event = repo.create_one(creator=user, event_data=event_data)
    return build_response(event)


event_router = APIRouter(prefix="/{event_id}")
event_id = Path(description="The id of the event")


def get_event(
    repo: EventsRepoDep, event_id: int = Path(description="The id of the event")
):
    event = cast(EventModel, repo.get_by_id(event_id))
    if event is None:
        raise NotFoundException()

    return event


EventDep = Annotated[EventModel, Depends(get_event)]


@event_router.get(
    "/", name="event-details", response_model=CustomResponse[EventDetailsSchema]
)
def get_event_details(
    request: Request,
    event: EventDep,
    staff_repo: StaffRepoDep,
    company_repo: CompaniesRepoDep,
):
    """
    Gets the details of an event
    """

    user: UserModel = request.user

    staff = staff_repo.get_by_column(StaffModel.user_id == user.id)
    if staff:
        if event.company_id != staff.company_id:
            raise UnauthorisedException()
    else:
        exists = company_repo.exists(
            CompanyModel.id == event.company_id, CompanyModel.owner_id == user.id
        )
        if not exists:
            raise UnauthorisedException()

    return build_response(event)


@event_router.get(
    "/attendees/",
    name="event-attendees",
    response_model=CustomResponse[list[EventAttendeeSchema]],
)
def get_event_attendees(
    request: Request, event: EventDep, repo: AttendeesRepoDep, staff_repo: StaffRepoDep
):
    """
    Gets the attendees of this event
    """

    user: UserModel = request.user
    staff = staff_repo.get_by_column(StaffModel.user_id == user.id)
    if staff:
        if event.company_id != staff.company_id:
            raise UnauthorisedException()
    else:
        # Check if user is owner
        if cast(int, event.company.owner_id) != user.id:
            raise UnauthorisedException()

    if staff and staff.has_role(StaffRole.scanner):
        # attendees = repo.get_all(EventAttendeeModel.ticket.scanned_by_id == staff.id)
        attendees = (
            repo.query()
            .join(EventTicketModel)
            .filter(EventTicketModel.scanned_by_id == staff.id)
        )
    else:
        attendees = repo.get_all(EventAttendeeModel.event_id == event.id)

    return build_response(attendees)


@event_router.post(
    "/attendees/",
    name="event-attendees-create",
    response_model=CustomResponse[EventAttendeeSchema],
)
def add_event_attendee(
    request: Request,
    attendee_data: EventAttendeeCreateSchema,
    event: EventDep,
    repo: AttendeesRepoDep,
    table_repo: EventTablesRepoDep,
    company_repo: CompaniesRepoDep,
    staff_repo: StaffRepoDep,
    background_task: BackgroundTasks,
):
    user = request.user

    company_id = event.company_id
    db_company = cast(CompanyModel, company_repo.get_by_id(company_id))
    if db_company is None:
        raise NotFoundException("This company does not exists")

    staff = staff_repo.get_by_column(StaffModel.user_id == user.id)
    if staff:
        if not (
            staff.has_role(StaffRole.creator)
            and cast(int, staff.company_id) == company_id
        ):
            raise UnauthorisedException()
    else:
        # Check if user is owner
        if cast(int, db_company.owner_id) != user.id:
            raise UnauthorisedException()

    table_id = attendee_data.table_id
    table_name: str | None = None
    if table_id is not None:
        table = cast(EventTableModel | None, table_repo.get_by_id(table_id))
        if table is not None:
            table_name = table.name

    attendee = repo.create_one(attendee_data, event, db_company, table_name)
    if attendee is None:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Could not create the attendee",
        )

    background_task.add_task(send_event_ticket, event.name, attendee.ticket.id)
    return build_response(attendee)


@event_router.post(
    "/ticket-scan/",
    name="ticket-scan",
    response_model=CustomResponse[EventAttendeeSchema],
)
def scan_ticket(
    request: Request,
    code: Annotated[str, Body(embed=True)],
    event: EventDep,
    repo: TicketsRepoDep,
    staff_repo: StaffRepoDep,
    background_task: BackgroundTasks,
):
    event_end = cast(datetime, event.date_to) + timedelta(days=1)
    now = datetime.now(pendulum.UTC)
    if event.status == EventStatus.ended or now > event_end:
        raise BadRequestException("This event has ended")

    user = request.user
    staff = staff_repo.get_by_column(StaffModel.user_id == user.id)
    if not staff:
        raise UnauthorisedException()

    if event.company_id != staff.company_id:
        raise UnauthorisedException()

    ticket = repo.get_by_column(
        EventTicketModel.code == code, EventTicketModel.event_id == event.id
    )
    if ticket is None:
        raise NotFoundException("This ticket was not found")

    if ticket.is_scanned:
        raise BadRequestException(
            "This ticket has already been scanned",
            data={"at": ticket.scanned_at, "by": ticket.scanned_by.user.name},
        )

    ticket = repo.scan_ticket(ticket, scanned_by_id=staff.id)
    attendee = ticket.attendee

    background_task.add_task(notify_user_of_ticket_scan, event.name, attendee.ticket.id)
    return build_response(attendee)


@event_router.get(
    "/tables/",
    name="event-tables",
    response_model=CustomResponse[list[EventTableSchema]],
)
def get_event_tables(
    request: Request,
    event: EventDep,
    repo: EventTablesRepoDep,
    staff_repo: StaffRepoDep,
):
    """
    Gets the attendees of this event
    """

    user: UserModel = request.user
    staff = staff_repo.get_by_column(StaffModel.user_id == user.id)
    if staff:
        if event.company_id != staff.company_id:
            raise UnauthorisedException()
    else:
        # Check if user is owner
        if cast(int, event.company.owner_id) != user.id:
            raise UnauthorisedException()

    tables = repo.get_all(EventTableModel.event_id == event.id)
    return build_response(tables)


router.include_router(event_router)
