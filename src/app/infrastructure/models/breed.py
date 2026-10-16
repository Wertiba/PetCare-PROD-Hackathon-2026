import uuid

from sqlalchemy import Enum as SAEnum
from sqlalchemy import String, UniqueConstraint
from sqlalchemy.dialects.postgresql import UUID as PGUUID
from sqlalchemy.orm import Mapped, mapped_column

from app.core.enums import PetType
from app.infrastructure.models.base import Base

PET_TYPE_ENUM = SAEnum(
    PetType,
    name="pet_type",
    native_enum=False,
    length=20,
    values_callable=lambda enum_cls: [member.value for member in enum_cls],
)


class Breed(Base):
    __tablename__ = "breeds"
    __table_args__ = (UniqueConstraint("type", "name", name="uq_breeds_type_name"),)

    id: Mapped[uuid.UUID] = mapped_column(PGUUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    type: Mapped[PetType] = mapped_column(PET_TYPE_ENUM, nullable=False)
    name: Mapped[str] = mapped_column(String(100), nullable=False)
