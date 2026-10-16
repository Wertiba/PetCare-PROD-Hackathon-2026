from typing import Annotated

from fastapi import Depends

from app.api.v1.dependencies.uow import UnitOfWorkDep
from app.services import PetService


def get_pet_service(uow: UnitOfWorkDep) -> PetService:
    return PetService(uow)


PetServiceDep = Annotated[PetService, Depends(get_pet_service)]
