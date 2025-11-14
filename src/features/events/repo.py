from datetime import datetime
import io
from typing import cast

import pendulum

from src.common.exceptions import UniqueValidationError
from src.common.repo import RepoBase
from src.common.utils.token import generate_token
from src.core.config import default_company_logo_path
from src.core.storage.backend import storage_backend
from src.features.auth.models import UserModel
from src.features.companies.models import CompanyModel
from src.features.events.schemas import (EventAttendeeCreateSchema,
                                         EventCreateSchema)
from src.features.events.utils.ticket import generate_ticket

from .models import (EventAttendeeModel, EventModel, EventTableModel,
                     EventTicketModel)


class EventsRepo(RepoBase[EventModel]):
    model = EventModel

    def create_one(self, creator: UserModel, event_data: EventCreateSchema):
        db = self.db

        event_dict = event_data.model_dump()
        tables = cast(list[str], event_dict.pop('tables'))

        tables = [EventTableModel(name=table_name) for table_name in tables]
        event = EventModel(**event_dict,
                           created_by_id=creator.id,
                           tables=tables)

        db.add(event)
        db.commit()
        db.refresh(event)
        return event

class EventTablesRepo(RepoBase[EventTableModel]):
    model = EventTableModel

class TicketsRepo(RepoBase[EventTicketModel]):
    model = EventTicketModel

    def scan_ticket(self, ticket: EventTicketModel, scanned_by_id: int):
        db = self.db

        ticket.scanned_by_id = scanned_by_id
        ticket.scanned_at = datetime.now(pendulum.UTC)
        db.add(ticket)
        db.commit()
        db.refresh(ticket)

        return ticket

class AttendeesRepo(RepoBase[EventAttendeeModel]):
    model = EventAttendeeModel

    def create_one(self,
                   attendee_data: EventAttendeeCreateSchema,
                   event: EventModel,
                   company: CompanyModel,
                   table_name: str | None):
        db = self.db

        max_trials = 10
        trial = 0
        code: str | None = None
        while trial < max_trials:
            trial += 1

            generated_code = generate_token()
            q = db.query(EventTicketModel).filter(EventTicketModel.code == generated_code)
            if db.query(q.exists()).scalar():
                continue

            code = generated_code

        if code is None:
            return None

        attendee_dict = attendee_data.model_dump()
        table_id: int | None = attendee_dict.get('table_id')
        if table_id is not None:
            attendee_dict.pop('table_id')

        logo_path = company.logo_path
        logo_bytes: bytes | None = None
        if logo_path is not None:
            logo_bytes = storage_backend.get_file(logo_path)

        if logo_bytes is None:
            with open(default_company_logo_path, 'rb') as f:
                logo_bytes = f.read()

        logo = io.BytesIO(logo_bytes)
        attendee_dict['table'] = table_name
        url = generate_ticket(code,
                              logo=logo,
                              event_name=event.name,
                              event_venue=event.venue,
                              event_date=event.date_from,
                              attendees_data=[attendee_dict],
                              company_id=company.id,
                              event_id=event.id)

        attendee_dict.pop('table')
        price = attendee_dict.pop('price')
        try:
            ticket = EventTicketModel(code=code,
                                      url=url,
                                      price=price,
                                      event_id=event.id,
                                      table_id=table_id)
            db.add(ticket)

            attendee = EventAttendeeModel(**attendee_dict,
                                          event_id=event.id,
                                          ticket=ticket)
            db.add(attendee)

            db.commit()
            db.refresh(attendee)
        except UniqueValidationError as e:
            raise UniqueValidationError(detail='This attendee already exists')
        except Exception as e:
            db.rollback()
            raise e

        return attendee

