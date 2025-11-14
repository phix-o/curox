from fastapi import File, UploadFile
from pydantic import BaseModel, Field

from src.common.schemas import BaseModelSchema
from src.features.companies.models import StaffRole
from src.features.auth.schemas import UserSchema

# Staff
class StaffCreate(BaseModel):
    role: StaffRole

class Staff(BaseModelSchema, BaseModel):
    pass

class StaffDetailsSchema(BaseModelSchema, BaseModel):
    role: StaffRole
    user: UserSchema


# Company
class CompanyBase(BaseModel):
    name: str = Field(min_length=2, max_length=30)

class CompanyCreate(CompanyBase):
    pass

class CompanyUpdateSchema(CompanyBase):
    pass

class Company(BaseModelSchema, CompanyBase):
    pass


class CompanyDetailsSchema(BaseModelSchema, CompanyBase):
    owner: UserSchema
    logo_url: str
    staff: list[StaffDetailsSchema]

# Dashboard data
class CompanySummary(BaseModel):
    events_count: int
