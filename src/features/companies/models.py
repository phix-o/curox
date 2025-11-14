import enum
from typing import cast

from sqlalchemy import Column, Enum, ForeignKey, Integer, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from src.core.database import Base
from src.core.storage.backend import storage_backend


class CompanyModel(Base):
    __tablename__ = 'companies'

    name: Mapped[str] = mapped_column(String(length=30))
    logo_path: Mapped[str] = mapped_column()
    owner_id: Mapped[int] = mapped_column(ForeignKey('users.id'))

    staff = relationship('StaffModel', back_populates='company')
    owner = relationship('UserModel', back_populates='companies')
    events = relationship('EventModel', back_populates='company')

    @property
    def logo_url(self) -> str:
        return cast(str, storage_backend.get_url(self.logo_path))


class StaffRole(enum.Enum):
    admin = 'AD'        # Company owner
    creator = 'CR'      # Can create events
    scanner = 'SC'      # Can create events

class StaffModel(Base):
    __tablename__ = 'staff'

    role = Column(Enum(StaffRole), default=StaffRole.scanner, nullable=False)
    user_id = Column(Integer, ForeignKey('users.id'), unique=True, nullable=False)
    company_id = Column(Integer, ForeignKey('companies.id'), nullable=False)

    user = relationship('UserModel', back_populates='staff')
    company = relationship('CompanyModel', back_populates='staff')
    scanned_tickets = relationship('EventTicketModel', back_populates='scanned_by')

    def has_role(self, role: StaffRole) -> bool:
        return bool(self.role == role)

