from datetime import datetime
from typing import cast

from sqlalchemy import DateTime, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from src.core.auth.auth import hash_password, verify_password
from src.core.database import Base
from src.core.storage.backend import storage_backend


class UserModel(Base):
    __tablename__ = 'users'

    email: Mapped[str] = mapped_column(unique=True, index=True)
    first_name: Mapped[str | None] = mapped_column()
    last_name: Mapped[str | None] = mapped_column()
    password: Mapped[str] = mapped_column()
    phone_number: Mapped[str | None] = mapped_column(String(20), unique=True)
    is_active: Mapped[bool] = mapped_column(default=True)
    avatar_path: Mapped[str | None] = mapped_column()
    should_reset_password: Mapped[bool | None] = mapped_column(default=True)
    password_reset_token: Mapped[str | None] = mapped_column(String(length=10))
    password_reset_token_expiry: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))

    staff = relationship('StaffModel', uselist=False, back_populates='user')
    companies = relationship('CompanyModel', back_populates='owner')
    events_created = relationship('EventModel', back_populates='created_by')

    @property
    def avatar_url(self):
        return storage_backend.get_url(self.avatar_path)

    @property
    def name(self):
        f_name = self.first_name
        l_name = self.last_name
        if f_name and l_name:
            name = f'{f_name} {l_name}'
        elif l_name:
            name = f'{l_name}'

        return name

    def set_password(self, password: str) -> None:
        hashed_password = hash_password(password)
        self.password = hashed_password

    def check_password(self, password: str) -> bool:
        return verify_password(password, cast(str, self.password))

