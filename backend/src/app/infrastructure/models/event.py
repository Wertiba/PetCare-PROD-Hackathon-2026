import uuid
from datetime import datetime, timezone

from sqlalchemy import ForeignKey, Index, String
from sqlalchemy.dialects.postgresql import TIMESTAMP
from sqlalchemy.dialects.postgresql import UUID as PGUUID
from sqlalchemy.orm import Mapped, mapped_column

from app.core.enums import EventPeriod, EventStatus, EventType
from app.infrastructure.models.base import Base, str_enum


class Event(Base):
    """A planned or past procedure: vaccination, parasite treatment, vet visit, medication..."""

    __tablename__ = "events"
    __table_args__ = (
        Index("idx_events_pet_id", "pet_id"),
        Index("idx_events_status_schedule", "status", "schedule"),
    )

    id: Mapped[uuid.UUID] = mapped_column(PGUUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    pet_id: Mapped[uuid.UUID] = mapped_column(
        PGUUID(as_uuid=True),
        ForeignKey("pets.id", ondelete="CASCADE"),
        nullable=False,
    )
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    type: Mapped[EventType] = mapped_column(str_enum(EventType, "event_type", length=30), nullable=False)
    status: Mapped[EventStatus] = mapped_column(str_enum(EventStatus, "event_status"), nullable=False)
    schedule: Mapped[datetime] = mapped_column(TIMESTAMP(timezone=True, precision=6), nullable=False)
    period: Mapped[EventPeriod] = mapped_column(str_enum(EventPeriod, "event_period"), nullable=False)
    description: Mapped[str | None] = mapped_column(String(2000), nullable=True)
    done_at: Mapped[datetime | None] = mapped_column(TIMESTAMP(timezone=True, precision=6), nullable=True)
    created_at: Mapped[datetime] = mapped_column(
        TIMESTAMP(timezone=True, precision=6),
        nullable=False,
        default=lambda: datetime.now(timezone.utc),
    )
    updated_at: Mapped[datetime] = mapped_column(
        TIMESTAMP(timezone=True, precision=6),
        nullable=False,
        default=lambda: datetime.now(timezone.utc),
    )
