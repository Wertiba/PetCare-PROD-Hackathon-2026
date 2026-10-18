from sqlalchemy import Select, exists, func, select, update
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.application.exceptions import ApplicationError
from app.application.ports.notification_gateway import NotificationGateway
from app.domain.events.entity import Event
from app.domain.events.ids import EventId
from app.domain.notifications.entity import Notification
from app.domain.notifications.enums import NotificationStatus
from app.domain.notifications.ids import NotificationId
from app.domain.notifications.settings import NotificationSettings, WebPushSubscription
from app.domain.pets.entity import Pet
from app.domain.pets.ids import PetId
from app.domain.users.ids import UserId


class SqlAlchemyNotificationGateway(NotificationGateway):
    def __init__(self, session: AsyncSession) -> None:
        self.session = session

    async def get_by_id(self, id_: NotificationId, *, user_id: UserId | None = None) -> Notification | None:
        stmt = select(Notification).where(Notification.id == id_)
        if user_id is not None:
            stmt = self._owned(stmt, user_id)
        try:
            result = await self.session.execute(stmt)
            return result.scalar_one_or_none()
        except SQLAlchemyError as exc:
            raise ApplicationError("Database error") from exc

    async def get_by_user_id(
        self,
        user_id: UserId,
        now: float,
        offset: int,
        limit: int,
        *,
        event_id: EventId | None = None,
        pet_id: PetId | None = None,
        status: NotificationStatus | None = None,
        due: bool = False,
    ) -> list[Notification]:
        stmt = self._apply_criteria(
            self._owned(select(Notification), user_id), now, event_id=event_id, pet_id=pet_id, status=status, due=due
        )
        stmt = stmt.order_by(Notification.time.desc()).offset(offset).limit(limit)
        try:
            result = await self.session.execute(stmt)
            return list(result.scalars().all())
        except SQLAlchemyError as e:
            raise ApplicationError("Database error") from e

    async def list_pending_undelivered(self, *, now: float, earliest: float) -> list[Notification]:
        # Users without the channel stay pending and can still be sent inside MAX_LATENESS.
        has_subscription = exists().where(WebPushSubscription.user_id == Pet.user_id)
        stmt = (
            select(Notification)
            .options(selectinload(Notification.event).selectinload(Event.pet))
            .join(Event, Event.id == Notification.event_id)
            .join(Pet, Pet.id == Event.pet_id)
            .join(NotificationSettings, NotificationSettings.user_id == Pet.user_id)
            .where(
                Notification.status == NotificationStatus.PENDING,
                Notification.delivered_at.is_(None),
                Notification.time <= now,
                Notification.time >= earliest,
                NotificationSettings.web_push_enabled.is_(True),
                has_subscription,
            )
            .order_by(Notification.time.asc())
        )
        try:
            result = await self.session.execute(stmt)
            return list(result.scalars().all())
        except SQLAlchemyError as exc:
            raise ApplicationError("Database error") from exc

    async def claim_delivery(self, notification_id: NotificationId, delivered_at: float) -> bool:
        # Conditional update is the cross-worker lock. RETURNING one id is rowcount == 1.
        # synchronize_session=False keeps a stale identity-map copy from writing delivered_at back to NULL.
        stmt = (
            update(Notification)
            .where(Notification.id == notification_id, Notification.delivered_at.is_(None))
            .values(delivered_at=delivered_at)
            .returning(Notification.id)
            .execution_options(synchronize_session=False)
        )
        try:
            result = await self.session.execute(stmt)
            claimed = result.scalar_one_or_none() is not None
            await self.session.commit()
        except SQLAlchemyError as exc:
            raise ApplicationError("Database error") from exc
        return claimed

    async def release_delivery(self, notification_id: NotificationId, claimed_at: float) -> None:
        # Same claimed_at guard as the lock: a newer claim from another worker is left alone.
        stmt = (
            update(Notification)
            .where(Notification.id == notification_id, Notification.delivered_at == claimed_at)
            .values(delivered_at=None)
            .execution_options(synchronize_session=False)
        )
        try:
            await self.session.execute(stmt)
            await self.session.commit()
        except SQLAlchemyError as exc:
            raise ApplicationError("Database error") from exc

    async def count_by_user_id(
        self,
        user_id: UserId,
        now: float,
        *,
        event_id: EventId | None = None,
        pet_id: PetId | None = None,
        status: NotificationStatus | None = None,
        due: bool = False,
    ) -> int:
        stmt = self._apply_criteria(
            self._owned(select(func.count()).select_from(Notification), user_id),
            now,
            event_id=event_id,
            pet_id=pet_id,
            status=status,
            due=due,
        )
        try:
            result = await self.session.execute(stmt)
            return result.scalar_one()
        except SQLAlchemyError as e:
            raise ApplicationError("Database error") from e

    @staticmethod
    def _owned(stmt: Select, user_id: UserId) -> Select:
        return (
            stmt.join(Event, Event.id == Notification.event_id)
            .join(Pet, Pet.id == Event.pet_id)
            .where(Pet.user_id == user_id)
        )

    @staticmethod
    def _apply_criteria(
        stmt: Select,
        now: float,
        *,
        event_id: EventId | None = None,
        pet_id: PetId | None = None,
        status: NotificationStatus | None = None,
        due: bool = False,
    ) -> Select:
        if event_id is not None:
            stmt = stmt.where(Notification.event_id == event_id)
        if pet_id is not None:
            stmt = stmt.where(Event.pet_id == pet_id)
        if status is not None:
            stmt = stmt.where(Notification.status == status)
        if due:
            stmt = stmt.where(Notification.status == NotificationStatus.PENDING, Notification.time <= now)
        return stmt
