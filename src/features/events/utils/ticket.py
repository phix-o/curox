import io
from datetime import datetime
from typing import cast

import pendulum
from fastapi import UploadFile

from src.core.database import SessionLocal
from src.core.logger import logger
from src.core.mail import send_email
from src.core.sms import send_sms
from src.core.storage.backend import storage_backend
from src.features.events.models import EventModel, EventTicketModel

from .pdf import generate_pdf


def generate_ticket(
    code: str,
    logo: io.BytesIO,
    event_name: str,
    event_venue: str,
    event_date: datetime,
    attendees_data: list[dict],
    company_id: int,
    event_id: int,
) -> str:
    """
    Generates and saves the ticket pdf sent to the client
    """

    pdf_file = io.BytesIO()
    try:
        generate_pdf(
            pdf_file,
            logo=logo,
            code=code,
            event_name=event_name,
            event_venue=event_venue,
            event_date=event_date,
            table_records=attendees_data,
        )

        path = (
            f"/companies/{company_id}/tickets/{event_id}/ticket_{event_id}_{code}.pdf"
        )
        url = storage_backend.upload_file(pdf_file, path)
    finally:
        pdf_file.close()

    return url


async def send_event_ticket(event_name: str, ticket_id: int):
    logger.info("Sending event ticket '{}': '{}'", event_name, ticket_id)

    db = SessionLocal()
    try:
        ticket = (
            db.query(EventTicketModel).filter(EventTicketModel.id == ticket_id).first()
        )
        if ticket is None:
            return

        subject = event_name
        to: str = ticket.attendee.email

        ticket_file = storage_backend.get_file(ticket.url)
        if ticket_file is None:
            return

        file_io = io.BytesIO(ticket_file)
        prepared_event_name = event_name.replace(" ", "_").lower()
        filename = f"{prepared_event_name}_ticket.pdf"
        attachment = UploadFile(file=file_io, filename=filename)
        try:
            event = cast(EventModel, ticket.event)
            from_date = pendulum.instance(event.date_from).format("dddd, MMMM Do, YYYY")
            await send_email(
                subject=subject,
                to=[to],
                attachments=[attachment],
                context={"name": event_name, "venue": event.venue, "from": from_date},
                template_name="events/new-ticket.html",
            )
            ticket.sent_at = datetime.now(pendulum.UTC)
            db.add(ticket)
            db.commit()
        finally:
            file_io.close()
    finally:
        db.close()


async def notify_user_of_ticket_scan(event_name: str, ticket_id: int):
    """
    Notifies the user by sms when their ticket has been scanned
    """

    logger.info("Notifying user of ticket scan: '{}'", ticket_id)

    db = SessionLocal()
    try:
        ticket = (
            db.query(EventTicketModel).filter(EventTicketModel.id == ticket_id).first()
        )
        if ticket is None:
            return

        to: str = ticket.attendee.email
        message = f"""
Welcome to the event: {event_name}.
Your ticket has successfully been scanned. Enjoy the event!.
        """.strip()

        await send_sms(message, to)
    finally:
        db.close()
