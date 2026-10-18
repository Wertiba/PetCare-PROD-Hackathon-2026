from sqlalchemy import select
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.ext.asyncio import AsyncSession

from app.application.exceptions import ApplicationError
from app.application.ports.web_push_subscription_gateway import WebPushSubscriptionGateway
from app.domain.notifications.settings import WebPushSubscription
from app.domain.users.ids import UserId


class SqlAlchemyWebPushSubscriptionGateway(WebPushSubscriptionGateway):
    def __init__(self, session: AsyncSession) -> None:
        self.session = session

    async def list_by_user_id(self, user_id: UserId) -> list[WebPushSubscription]:
        stmt = (
            select(WebPushSubscription)
            .where(WebPushSubscription.user_id == user_id)
            .order_by(WebPushSubscription.created_at.asc())
        )
        try:
            result = await self.session.execute(stmt)
            return list(result.scalars().all())
        except SQLAlchemyError as exc:
            raise ApplicationError("Database error") from exc

    async def get_by_endpoint(self, endpoint: str) -> WebPushSubscription | None:
        stmt = select(WebPushSubscription).where(WebPushSubscription.endpoint == endpoint)
        try:
            result = await self.session.execute(stmt)
            return result.scalar_one_or_none()
        except SQLAlchemyError as exc:
            raise ApplicationError("Database error") from exc
