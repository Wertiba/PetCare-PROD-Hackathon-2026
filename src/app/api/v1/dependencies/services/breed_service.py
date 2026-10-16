from typing import Annotated

from fastapi import Depends

from app.api.v1.dependencies.uow import UnitOfWorkDep
from app.services import BreedService


def get_breed_service(uow: UnitOfWorkDep) -> BreedService:
    return BreedService(uow)


BreedServiceDep = Annotated[BreedService, Depends(get_breed_service)]
