from typing import Any
from pydantic import BaseModel, EmailStr, Field

from src.common.schemas import BaseModelSchema
from src.core.storage.backend import storage_backend


class UserBase(BaseModel):
    email: EmailStr        = Field(max_length=40, examples=['kikia@ac.ac'])
    first_name: str | None = Field(default=None,
                                   max_length=40,
                                   description="The user's first name",
                                   examples=['Jane'])
    last_name: str | None  = Field(default=None,
                                   max_length=40,
                                   description="The user's last name",
                                   examples=['Doe'])

class UserCreate(UserBase):
    phone_number: str | None = Field(default=None,
                                     min_length=8,
                                     max_length=16,
                                     examples=['254:00000000'])
    password: str

class UserLogin(BaseModel):
    email: EmailStr = Field(max_length=40, examples=['kikia@ac.ac'])
    password: str

class UserSchema(BaseModelSchema, UserBase):
    phone_number: str | None

class UserDetailsSchema(BaseModelSchema, UserBase):
    phone_number: str | None
    is_active: bool
    avatar_url: str | None = Field(description="The user's avatar path")

class EmailVerifySchema(BaseModel):
    email: EmailStr = Field(description="The user's email")

class PasswordResetSchema(BaseModel):
    email: EmailStr = Field(description="The user's email")
    token: str      = Field(description='The token sent via email')
    password: str   = Field(description='The new password')

