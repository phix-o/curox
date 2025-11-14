from datetime import datetime

from sqlalchemy import DateTime, Integer, create_engine
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import (Mapped, Session, declarative_base, mapped_column,
                            sessionmaker)

from src.common.exceptions import UniqueValidationError
from src.core.config import settings

engine = create_engine(settings.db_url, echo=False)


class DBSession(Session):
    def commit(self) -> None:
        try:
            super().commit()
        except IntegrityError as e:
            # TODO: Handle every error gracefully
            print(e)
            raise UniqueValidationError()

SessionLocal = sessionmaker(class_=DBSession,
                            autocommit=False,
                            autoflush=False,
                            bind=engine)


class BaseModelMixin:
    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)

    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True),
                                                 nullable=False,
                                                 default=datetime.now)
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True),
                                                 nullable=False,
                                                 default=datetime.now,
                                                 onupdate=datetime.now)

Base = declarative_base(cls=BaseModelMixin)

