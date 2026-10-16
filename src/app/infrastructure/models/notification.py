import uuid
from datetime import datetime, timezone

from sqlalchemy import ForeignKey, Index
from sqlalchemy.dialects.postgresql import TIMESTAMP
from sqlalchemy.dialects.postgresql import UUID as PGUUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.enums import NotificationStatus, NotificationType
from app.infrastructure.models.base import Base, str_enum
from app.infrastructure.models.event import Event


class Notification(Base):
    """A reminder about an event, delivered through one channel at a given time."""

    __tablename__ = "notifications"
    __table_args__ = (
        Index("idx_notifications_event_id", "event_id"),
        Index("idx_notifications_status_time", "status", "time"),
    )

    id: Mapped[uuid.UUID] = mapped_column(PGUUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    event_id: Mapped[uuid.UUID] = mapped_column(
        PGUUID(as_uuid=True),
        ForeignKey("events.id", ondelete="CASCADE"),
        nullable=False,
    )
    type: Mapped[NotificationType] = mapped_column(
        str_enum(NotificationType, "notification_type"), nullable=False
    )
    status: Mapped[NotificationStatus] = mapped_column(
        str_enum(NotificationStatus, "notification_status"), nullable=False
    )
    time: Mapped[datetime] = mapped_column(TIMESTAMP(timezone=True, precision=6), nullable=False)
    created_at: Mapped[datetime] = mapped_column(
        TIMESTAMP(timezone=True, precision=6),
        nullable=False,
        default=lambda: datetime.now(timezone.utc),
    )

    event: Mapped[Event] = relationship(lazy="selectin")
