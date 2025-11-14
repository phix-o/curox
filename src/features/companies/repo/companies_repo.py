import random
from typing import cast

from fastapi import UploadFile

from src.common.repo import RepoBase
from src.core.storage.backend import storage_backend
from src.features.auth.models import UserModel
from src.features.companies.schemas import CompanyUpdateSchema

from ..models import CompanyModel


class CompaniesRepo(RepoBase[CompanyModel]):
    model = CompanyModel

    def _get_logo_path(self, company_id: int, filename: str) -> str:
        return f'/companies/{company_id}/images/logo_{random.randint(1024, 10024)}_{filename}'

    def update(self, company_data: CompanyUpdateSchema, company: CompanyModel):
        db = self.db

        company.name = company_data.name
        db.add(company)
        db.commit()
        db.refresh(company)

        return company

    def create_one(self, owner: UserModel, name: str, logo: UploadFile):
        db = self.db

        # This is okay because the path will be set correctly when uploading the logo
        path = 'temp-path'
        db_company = CompanyModel(
            name = name,
            logo_path = path,
            owner_id = owner.id
        )

        db.add(db_company)
        db.commit()
        db.refresh(db_company)

        try:
            company_id = db_company.id
            file_path = self._get_logo_path(company_id, cast(str, logo.filename))
            path = storage_backend.upload_file(logo.file, file_path)
            db_company.logo_path = path
            db.add(db_company)
            db.commit()
        except Exception as e:
            db.delete(db_company)
            db.commit()
            raise e

        return db_company

    def update_logo(self, company: CompanyModel, logo: UploadFile):
        db = self.db

        url = None
        try:
            company_id = company.id
            file_path = self._get_logo_path(company_id, cast(str, logo.filename))
            path = storage_backend.upload_file(logo.file, file_path)
            company.logo_path = path
            db.add(company)
            db.commit()
        except Exception as e:
            db.rollback()
            raise e

        url = storage_backend.get_url(path)
        return url
