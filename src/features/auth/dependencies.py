from typing import Annotated

from fastapi import Depends

from src.common.repo import get_repo

from .repo import UserRepo

UserRepoDep = Annotated[UserRepo, Depends(get_repo(UserRepo))]
