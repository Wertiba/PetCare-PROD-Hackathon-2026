from typing import Annotated

from fastapi import Depends

from app.api.v1.dependencies.uow import UnitOfWorkDep
from app.services import StateService


def get_state_service(uow: UnitOfWorkDep) -> StateService:
    return StateService(uow)


StateServiceDep = Annotated[StateService, Depends(get_state_service)]
