from typing import Generic, TypeVar, Generator

from sqlalchemy import ColumnExpressionArgument
from sqlalchemy.orm import Query, Session

from src.core.database import BaseModelMixin, SessionLocal

T = TypeVar("T", bound=BaseModelMixin)


class RepoBase(Generic[T]):
    model: type[T]

    def __init__(self, db: Session):
        self.db = db

    def count(self, *criterion: ColumnExpressionArgument[bool]) -> int:
        return self.db.query(self.model).filter(*criterion).count()

    def query(self) -> Query[T]:
        return self.db.query(self.model)

    def get_by_id(self, id: int) -> T | None:
        model = self.model
        return self.db.query(model).filter(model.id == id).first()

    def get_by_column(self, *criterion: ColumnExpressionArgument[bool]) -> T | None:
        return self.db.query(self.model).filter(*criterion).first()

    def get_all(self, *criterion: ColumnExpressionArgument[bool]) -> list[T] | None:
        return self.db.query(self.model).filter(*criterion).all()

    def exists(self, *criterion: ColumnExpressionArgument[bool]) -> bool:
        q = self.db.query(self.model).filter(*criterion)
        return self.db.query(q.exists()).scalar()


def get_repo(repo_cls: type[RepoBase[T]]):
    def inner() -> Generator[RepoBase[T]]:
        db = SessionLocal()
        repo = repo_cls(db)
        try:
            yield repo
        finally:
            db.close()

    return inner
