import uuid
from datetime import datetime, timezone

from sqlalchemy import ForeignKey, Index, String
from sqlalchemy.dialects.postgresql import TIMESTAMP
from sqlalchemy.dialects.postgresql import UUID as PGUUID
from sqlalchemy.orm import Mapped, mapped_column

from app.core.enums import CategoryKind, CategoryType, CategoryUnit
from app.infrastructure.models.base import Base, str_enum


class Category(Base):
    """A tracked parameter (weight, food, walk...). created_by is NULL for built-in categories."""

    __tablename__ = "categories"
    __table_args__ = (Index("idx_categories_created_by", "created_by"),)

    id: Mapped[uuid.UUID] = mapped_column(PGUUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    name: Mapped[str] = mapped_column(String(100), nullable=False)
    kind: Mapped[CategoryKind] = mapped_column(str_enum(CategoryKind, "category_kind"), nullable=False)
    type: Mapped[CategoryType] = mapped_column(str_enum(CategoryType, "category_type"), nullable=False)
    unit: Mapped[CategoryUnit] = mapped_column(str_enum(CategoryUnit, "category_unit"), nullable=False)
    created_by: Mapped[uuid.UUID | None] = mapped_column(
        PGUUID(as_uuid=True),
        ForeignKey("users.id", ondelete="CASCADE"),
        nullable=True,
    )
    created_at: Mapped[datetime] = mapped_column(
        TIMESTAMP(timezone=True, precision=6),
        nullable=False,
        default=lambda: datetime.now(timezone.utc),
    )
