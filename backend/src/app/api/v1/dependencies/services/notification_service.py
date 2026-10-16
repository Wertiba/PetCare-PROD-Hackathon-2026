from typing import Annotated

from fastapi import Depends

from app.api.v1.dependencies.uow import UnitOfWorkDep
from app.services import NotificationService


def get_notification_service(uow: UnitOfWorkDep) -> NotificationService:
    return NotificationService(uow)


NotificationServiceDep = Annotated[NotificationService, Depends(get_notification_service)]
