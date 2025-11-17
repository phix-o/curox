from typing import Annotated, Any

from fastapi import Depends

from src.common.repo import get_repo

from src.core.cache import CacheDep

from .repo.companies_repo import CompaniesRepo
from .repo.staff_repo import StaffRepo 

CompaniesRepoDep = Annotated[CompaniesRepo, Depends(get_repo(CompaniesRepo))]
StaffRepoDep = Annotated[StaffRepo, Depends(get_repo(StaffRepo))]

CompaniesCacheDep = CacheDep[list[dict[str, Any]]]
