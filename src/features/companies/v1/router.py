from typing import Annotated, cast

from fastapi import (
    APIRouter,
    BackgroundTasks,
    Body,
    Depends,
    File,
    Form,
    Path,
    Request,
    UploadFile,
)

from src.common.exceptions import (
    BadRequestException,
    NotFoundException,
    UnauthorisedException,
)
from src.common.utils.responses import CustomResponse, build_response
from src.core.auth.bearer import JWTBearer
from src.core.cache import CacheDep
from src.features.auth.dependencies import UserRepoDep
from src.features.auth.models import UserModel
from src.features.auth.schemas import UserCreate
from src.features.companies.models import CompanyModel, StaffModel
from src.features.companies.schemas import (
    CompanyDetailsSchema,
    CompanySummary,
    CompanyUpdateSchema,
    StaffCreate,
    StaffDetailsSchema,
)
from src.features.events.dependencies import EventsRepoDep
from src.features.events.models import EventModel
from src.features.events.schemas import EventSchema

from ..dependencies import CompaniesRepoDep, StaffRepoDep
from ..utils import notify_staff_of_add

router = APIRouter(
    prefix="/companies", dependencies=[Depends(JWTBearer())], tags=["Companies"]
)


@router.get(
    "/",
    name="companies-list",
    response_model=CustomResponse[list[CompanyDetailsSchema]],
)
def list_companies(
    request: Request,
    repo: CompaniesRepoDep,
    staff_repo: StaffRepoDep,
    cache: CacheDep,
):
    user = request.user

    # Create cache key based on user and staff status
    as_staff = staff_repo.get_by_column(StaffModel.user_id == user.id)
    cache_key = f"companies:user:{user.id}:staff:{as_staff.id if as_staff else 'none'}"

    # Try to get from cache
    cached_companies = cache.get(cache_key)
    if cached_companies is not None:
        companies = [
            CompanyDetailsSchema.model_validate_json(company)
            for company in cached_companies
        ]
        return build_response(companies)

    # Fetch from database
    if as_staff:
        companies = repo.get_all(CompanyModel.id == as_staff.company_id)
    else:
        companies = repo.get_all(CompanyModel.owner_id == user.id)

    # Cache the result
    companies_to_cache = [
        CompanyDetailsSchema.model_validate(company).model_dump_json()
        for company in companies
    ]
    cache.set(cache_key, companies_to_cache)

    return build_response(companies)


@router.post(
    "/",
    name="companies-create",
    response_model=CustomResponse[CompanyDetailsSchema],
)
def create_company(
    request: Request,
    repo: CompaniesRepoDep,
    cache: CacheDep,
    name: Annotated[str, Form(description="The company name")],
    logo: Annotated[UploadFile, File(description="The company logo")],
):
    user: UserModel = request.user
    company = repo.create_one(user, name, logo)

    cache.clear_pattern(f"companies:user:{user.id}:*")
    return build_response(company)


company_router = APIRouter(prefix="/{company_id}")


def get_company(
    repo: CompaniesRepoDep, company_id: int = Path(description="The company id")
):
    company = repo.get_by_id(company_id)
    if company is None:
        raise NotFoundException("This company does not exist")

    return company


CompanyDep = Annotated[CompanyModel, Depends(get_company)]


@company_router.get(
    "/", name="company-details", response_model=CustomResponse[CompanyDetailsSchema]
)
def get_company_details(request: Request, company: CompanyDep):
    user = request.user
    if cast(int, company.owner_id) != user.id:
        raise UnauthorisedException()

    return build_response(company)


@company_router.patch(
    "/", name="company-update", response_model=CustomResponse[CompanyDetailsSchema]
)
def update_company_details(
    request: Request,
    company: CompanyDep,
    company_data: CompanyUpdateSchema,
    repo: CompaniesRepoDep,
):
    user = request.user
    if cast(int, company.owner_id) != user.id:
        raise UnauthorisedException()

    company = repo.update(company_data, company)
    return build_response(company)


@company_router.post("/logo/", name="company-logo", response_model=CustomResponse[str])
def update_avatar(
    request: Request,
    logo: Annotated[UploadFile, File(description="The company logo")],
    company: CompanyDep,
    repo: CompaniesRepoDep,
):
    user = request.user
    if user.id != company.owner_id:
        raise UnauthorisedException()

    url = repo.update_logo(company, logo)
    return build_response(url)


@company_router.get(
    "/staff/",
    name="company-staff-list",
    response_model=CustomResponse[list[StaffDetailsSchema]],
)
def list_company_staff(request: Request, company: CompanyDep, staff_repo: StaffRepoDep):
    user = request.user
    user_staff = staff_repo.get_by_column(StaffModel.user_id == user.id)
    if user_staff:
        if cast(int, user_staff.company_id) != company.id:
            raise UnauthorisedException()
    elif company.owner_id != user.id:
        raise UnauthorisedException()

    staff = staff_repo.get_all(StaffModel.company_id == company.id)
    return build_response(staff)


@company_router.post(
    "/staff/",
    name="company-staff-add",
    response_model=CustomResponse[StaffDetailsSchema | None],
)
def add_company_staff(
    request: Request,
    staff_data: Annotated[StaffCreate, Body(alias="staff")],
    user_data: Annotated[UserCreate, Body(alias="user")],
    company: CompanyDep,
    staff_repo: StaffRepoDep,
    background_task: BackgroundTasks,
    user_repo: UserRepoDep,
):
    user = request.user
    if cast(int, company.owner_id) != user.id:
        raise UnauthorisedException

    user_exists = user_repo.exists(UserModel.email == user_data.email)
    if user_exists:
        raise BadRequestException("A user with that email already exists")

    phone_number = user_data.phone_number
    if phone_number is not None:
        user_exists = user_repo.exists(UserModel.phone_number == user_data.phone_number)
        if user_exists:
            raise BadRequestException("A user with that phone number already exists")

    staff = staff_repo.create_one(company, user_data, staff_data)
    background_task.add_task(
        notify_staff_of_add,
        email=staff.user.email,
        password=user_data.password,
        company_name=company.name,
        adder_email=user.email,
    )

    return build_response(staff)


@company_router.get(
    "/events/",
    name="company-events-list",
    response_model=CustomResponse[list[EventSchema]],
)
def list_company_events(
    request: Request,
    company: CompanyDep,
    events_repo: EventsRepoDep,
    staff_repo: StaffRepoDep,
):
    """
    Lists the events belonging to a company
    """

    user: UserModel = request.user

    # Permissions
    staff = staff_repo.get_by_column(StaffModel.user_id == user.id)
    if staff:
        # check if this staff has access to this company
        exists = staff_repo.exists(
            StaffModel.user_id == user.id, StaffModel.company_id == company.id
        )
        if not exists:
            raise UnauthorisedException()
    else:
        # Check if this is the owner (who is not a staff member)
        if cast(int, company.owner_id) != user.id:
            raise UnauthorisedException()

    events = events_repo.get_all(EventModel.company_id == company.id)
    return build_response(events)


@company_router.get(
    "/summary/", name="company-summary", response_model=CustomResponse[CompanySummary]
)
def get_company_summary(
    request: Request,
    company: CompanyDep,
    events_repo: EventsRepoDep,
    staff_repo: StaffRepoDep,
):
    user = request.user
    as_staff = staff_repo.get_by_column(StaffModel.user_id == user.id)
    if as_staff:
        if as_staff.company_id != company.id:
            raise UnauthorisedException()
    elif company.owner_id != user.id:
        raise UnauthorisedException()

    events_count = events_repo.count(EventModel.company_id == company.id)

    return build_response({"events_count": events_count})


router.include_router(company_router)
