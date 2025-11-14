import enum
from datetime import datetime

from sqlalchemy import (
    DateTime,
    Enum,
    ForeignKey,
    Integer,
    String,
    Text,
    UniqueConstraint,
)
from sqlalchemy.orm import Mapped, mapped_column, relationship

from src.core.database import Base


class EventStatus(enum.Enum):
    active = "AC"
    cancelled = "CL"
    ended = "ED"


class EventModel(Base):
    __tablename__ = "events"

    name: Mapped[str] = mapped_column(String(length=100))
    venue: Mapped[str] = mapped_column(String(length=100))
    description: Mapped[str | None] = mapped_column(Text)
    date_from: Mapped[datetime] = mapped_column(DateTime(timezone=True))
    date_to: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
    status: Mapped[EventStatus] = mapped_column(
        Enum(EventStatus), default=EventStatus.active, nullable=True
    )

    company_id: Mapped[int] = mapped_column(Integer, ForeignKey("companies.id"))
    company = relationship("CompanyModel", uselist=False, back_populates="events")

    created_by_id: Mapped[int] = mapped_column(Integer, ForeignKey("users.id"))
    created_by: Mapped[int] = relationship(
        "UserModel", uselist=False, back_populates="events_created"
    )

    tables = relationship("EventTableModel", back_populates="event")
    tickets = relationship("EventTicketModel", back_populates="event")


class EventTableModel(Base):
    __tablename__ = "event_tables"

    name: Mapped[str] = mapped_column(String(length=10))
    event_id: Mapped[int] = mapped_column(ForeignKey("events.id"))

    __table_args__ = (UniqueConstraint("name", "event_id", name="uc_event_table"),)

    event = relationship("EventModel", back_populates="tables")
    tickets = relationship("EventTicketModel", back_populates="table")


class EventTicketModel(Base):
    __tablename__ = "event_tickets"

    code: Mapped[str] = mapped_column()
    url: Mapped[str] = mapped_column()
    price: Mapped[int] = mapped_column()
    event_id: Mapped[int] = mapped_column(ForeignKey("events.id"))
    table_id: Mapped[int | None] = mapped_column(ForeignKey("event_tables.id"))
    scanned_by_id: Mapped[int | None] = mapped_column(ForeignKey("staff.id"))
    scanned_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
    sent_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))

    __table_args__ = (
        UniqueConstraint("event_id", "code", name="uc_event_ticket_code"),
    )

    attendee = relationship(
        "EventAttendeeModel", uselist=False, back_populates="ticket"
    )
    event = relationship("EventModel", uselist=False, back_populates="tickets")
    scanned_by = relationship(
        "StaffModel", uselist=False, back_populates="scanned_tickets"
    )
    table = relationship("EventTableModel", uselist=False, back_populates="tickets")

    @property
    def is_scanned(self) -> bool:
        return self.scanned_by_id is not None


class EventAttendeeModel(Base):
    __tablename__ = "event_attendees"

    name: Mapped[str] = mapped_column()
    email: Mapped[str] = mapped_column(String(length=50))
    phone_number: Mapped[str | None] = mapped_column(String(length=20))
    event_id: Mapped[int] = mapped_column(ForeignKey("events.id"))
    ticket_id: Mapped[int] = mapped_column(
        ForeignKey("event_tickets.id"), nullable=True
    )

    __table_args__ = (UniqueConstraint("event_id", "email", name="uc_event_attendee"),)

    ticket = relationship("EventTicketModel", back_populates="attendee")
