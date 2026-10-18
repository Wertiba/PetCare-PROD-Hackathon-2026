from sqlalchemy import select
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.ext.asyncio import AsyncSession

from app.application.exceptions import ApplicationError
from app.application.ports.notification_settings_gateway import NotificationSettingsGateway
from app.domain.notifications.settings import NotificationSettings
from app.domain.users.ids import UserId


class SqlAlchemyNotificationSettingsGateway(NotificationSettingsGateway):
    def __init__(self, session: AsyncSession) -> None:
        self.session = session

    async def get_by_user_id(self, user_id: UserId) -> NotificationSettings | None:
        stmt = select(NotificationSettings).where(NotificationSettings.user_id == user_id)
        try:
            result = await self.session.execute(stmt)
            return result.scalar_one_or_none()
        except SQLAlchemyError as exc:
            raise ApplicationError("Database error") from exc
