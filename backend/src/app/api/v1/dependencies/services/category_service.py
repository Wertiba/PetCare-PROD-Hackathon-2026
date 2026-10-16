from typing import Annotated

from fastapi import Depends

from app.api.v1.dependencies.uow import UnitOfWorkDep
from app.services import CategoryService


def get_category_service(uow: UnitOfWorkDep) -> CategoryService:
    return CategoryService(uow)


CategoryServiceDep = Annotated[CategoryService, Depends(get_category_service)]
