from datetime import datetime
from typing import Annotated, cast

import pendulum
from fastapi import (
    APIRouter,
    BackgroundTasks,
    Body,
    File,
    HTTPException,
    Request,
    UploadFile,
    status,
)

from src.common.exceptions import BadRequestException, NotFoundException
from src.common.utils.responses import CustomResponse, build_response
from src.core.auth import TokenPair, create_token_pair
from src.core.logger import logger
from src.features.auth.models import UserModel
from src.features.auth.schemas import (
    EmailVerifySchema,
    PasswordResetSchema,
    UserCreate,
    UserDetailsSchema,
    UserLogin,
    UserSchema,
)
from src.features.auth.utils import notify_user_of_password_reset, send_token_to_user
from src.features.companies.dependencies import StaffRepoDep
from src.features.companies.models import StaffModel, StaffRole

from ..dependencies import UserRepoDep

router = APIRouter(prefix="/auth", tags=["Auth"])


@router.post("/token/", name="login", response_model=CustomResponse[TokenPair])
async def get_token(
    data: Annotated[UserLogin, Body()], repo: UserRepoDep, staff_repo: StaffRepoDep
):
    user = repo.get_by_column(UserModel.email == data.email)
    if user is None:
        raise BadRequestException("Incorrect email or password")

    if not user.check_password(data.password):
        raise BadRequestException("Incorrect email or password")

    role = StaffRole.admin
    as_staff = staff_repo.get_by_column(StaffModel.user_id == user.id)
    if as_staff:
        role = cast(StaffRole, as_staff.role)

    return build_response(create_token_pair(user.id, role))


@router.post("/signup/", name="signup", response_model=CustomResponse[UserSchema])
def signup(user: UserCreate, repo: UserRepoDep):
    db_user = repo.get_by_column(UserModel.email == user.email)
    if db_user is not None:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="User with that email already exists",
        )

    return build_response(repo.create_one(user))


@router.post(
    "/account-verification/",
    name="account-verification",
    response_model=CustomResponse[None],
)
async def verify_email(data: EmailVerifySchema, repo: UserRepoDep):
    email = data.email
    user = repo.get_by_column(UserModel.email == email)
    if user is None:
        raise NotFoundException("An account with this email address does not exists.")

    token = repo.generate_reset_token(user)
    await send_token_to_user(token, email)
    return build_response(None)


@router.post(
    "/password-reset/", name="password-reset", response_model=CustomResponse[None]
)
def reset_password(
    data: PasswordResetSchema, repo: UserRepoDep, background_tasks: BackgroundTasks
):
    token = data.token
    email = data.email
    user = repo.get_by_column(
        UserModel.password_reset_token == token, UserModel.email == email
    )
    if user is None:
        logger.error("User not found with {} and {}", email, token)
        raise BadRequestException("This token has expired or is invalid")

    now = datetime.now(pendulum.UTC)
    expiry = cast(datetime, user.password_reset_token_expiry)
    is_expired = now > expiry
    if is_expired:
        logger.error("Token expired: {} is greateer than {}", now, expiry)
        raise BadRequestException("This token has expired or is invalid")

    repo.update_password(user, data.password)
    background_tasks.add_task(notify_user_of_password_reset, email)

    return build_response(None)


@router.get(
    "/profile/", name="profile", response_model=CustomResponse[UserDetailsSchema]
)
def get_profile(request: Request):
    return build_response(request.user)


@router.post(
    "/profile/avatar/", name="profile-avatar", response_model=CustomResponse[str]
)
def update_avatar(
    request: Request,
    avatar: Annotated[UploadFile, File(description="The avatar file")],
    repo: UserRepoDep,
):
    # Find a better way to do this
    user = repo.get_by_id(request.user.id)
    if user is None:
        raise NotFoundException()

    url = repo.update_avatar(user, avatar)
    return build_response(url)
