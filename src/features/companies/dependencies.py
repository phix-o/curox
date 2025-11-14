
from typing import Annotated

from fastapi import Depends

from src.common.repo import get_repo

from .repo.companies_repo import CompaniesRepo
from .repo.staff_repo import StaffRepo 

CompaniesRepoDep = Annotated[CompaniesRepo, Depends(get_repo(CompaniesRepo))]
StaffRepoDep = Annotated[StaffRepo, Depends(get_repo(StaffRepo))]
