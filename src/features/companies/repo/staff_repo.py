
from src.common.repo import RepoBase
from src.features.auth.models import UserModel
from src.features.auth.schemas import UserCreate
from src.features.companies.models import CompanyModel, StaffModel
from src.features.companies.schemas import StaffCreate


class StaffRepo(RepoBase[StaffModel]):
    model = StaffModel

    def create_one(self,
                   company: CompanyModel,
                   user_data: UserCreate,
                   staff_data: StaffCreate):
        db = self.db

        try:
            db_user = UserModel(**user_data.model_dump())
            db_user.set_password(user_data.password)
            db.add(db_user)

            db_staff = StaffModel(**staff_data.model_dump(),
                                  user=db_user,
                                  company_id=company.id)
            db.add(db_staff)

            db.commit()
            db.refresh(db_staff)
        except Exception as exc:
            db.rollback()
            raise exc

        return db_staff

