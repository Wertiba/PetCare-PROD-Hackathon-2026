import uuid
from enum import Enum
from time import time

from sqlalchemy import JSON, Boolean, Column, Double, ForeignKey, Index, Integer, String, Table, UniqueConstraint
from sqlalchemy import Enum as SAEnum
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.dialects.postgresql import UUID as PGUUID
from sqlalchemy.orm import registry, relationship

from app.domain.animals.entity import Animal
from app.domain.breeds.entity import Breed
from app.domain.categories.entity import Category
from app.domain.categories.enums import CategoryKind, CategoryType, CategoryUnit
from app.domain.events.entity import Event
from app.domain.events.enums import EventPeriod, EventStatus, EventType
from app.domain.foods.entity import Food
from app.domain.notes.entity import Note
from app.domain.notifications.entity import Notification
from app.domain.notifications.enums import NotificationStatus, NotificationType
from app.domain.pets.entity import Pet
from app.domain.refresh_tokens.entity import RefreshToken
from app.domain.states.entity import State
from app.domain.users.entity import User
from app.domain.users.enums import UserRole

mapper_registry = registry()
metadata = mapper_registry.metadata


def str_enum(enum_cls: type[Enum], name: str, length: int = 20) -> SAEnum:
    """Enum stored as plain VARCHAR with lowercase values, like the rest of the schema."""
    return SAEnum(
        enum_cls,
        name=name,
        native_enum=False,
        length=length,
        values_callable=lambda cls: [member.value for member in cls],
    )


users = Table(
    "users",
    metadata,
    Column("id", PGUUID(as_uuid=True), primary_key=True, default=uuid.uuid4),
    Column("login", String(255), nullable=False, unique=True),
    Column("password", String(255), nullable=False),
    Column("full_name", String(255), nullable=False),
    Column(
        "role",
        SAEnum(
            UserRole,
            name="user_role",
            native_enum=False,
            length=20,
            values_callable=lambda enum_cls: [member.value for member in enum_cls],
        ),
        nullable=False,
    ),
    Column("is_active", Boolean, nullable=False, default=True),
    Column("created_by", PGUUID(as_uuid=True), ForeignKey("users.id"), nullable=True),
    Column("created_at", Double(), nullable=False, default=lambda: time()),
    Column("updated_at", Double(), nullable=False, default=lambda: time()),
)
animals = Table(
    "animals",
    metadata,
    Column("id", PGUUID(as_uuid=True), primary_key=True, default=uuid.uuid4),
    Column("name", String(100), nullable=False),
    Column("created_by", PGUUID(as_uuid=True), ForeignKey("users.id", ondelete="SET NULL"), nullable=True),
    Column("created_at", Double(), nullable=False, default=lambda: time()),
    UniqueConstraint("name", name="uq_animals_name"),
)
breeds = Table(
    "breeds",
    metadata,
    Column("id", PGUUID(as_uuid=True), primary_key=True, default=uuid.uuid4),
    Column("animal_id", PGUUID(as_uuid=True), ForeignKey("animals.id", ondelete="CASCADE"), nullable=False),
    Column("name", String(100), nullable=False),
    Column("created_by", PGUUID(as_uuid=True), ForeignKey("users.id", ondelete="SET NULL"), nullable=True),
    Column("created_at", Double(), nullable=False, default=lambda: time()),
    UniqueConstraint("animal_id", "name", name="uq_breeds_animal_id_name"),
)
pets = Table(
    "pets",
    metadata,
    Column("id", PGUUID(as_uuid=True), primary_key=True, default=uuid.uuid4),
    Column("user_id", PGUUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), nullable=False),
    Column("breed_id", PGUUID(as_uuid=True), ForeignKey("breeds.id", ondelete="SET NULL"), nullable=True),
    Column("name", String(100), nullable=False),
    Column("birth_date", Double, nullable=True),
    Column("photo_url", String(255), nullable=True),
    Column("created_at", Double(), nullable=False, default=lambda: time()),
    Column("updated_at", Double(), nullable=False, default=lambda: time()),
    Index("idx_pets_user_id", "user_id"),
)
categories = Table(
    "categories",
    metadata,
    Column("id", PGUUID(as_uuid=True), primary_key=True, default=uuid.uuid4),
    Column("name", String(100), nullable=False),
    Column("kind", str_enum(CategoryKind, "category_kind"), nullable=False),
    Column("type", str_enum(CategoryType, "category_type"), nullable=False),
    Column("unit", str_enum(CategoryUnit, "category_unit"), nullable=False),
    Column("created_by", PGUUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), nullable=True),
    Column("created_at", Double(), nullable=False, default=lambda: time()),
    Index("idx_categories_created_by", "created_by"),
)
states = Table(
    "states",
    metadata,
    Column("id", PGUUID(as_uuid=True), primary_key=True, default=uuid.uuid4),
    Column("pet_id", PGUUID(as_uuid=True), ForeignKey("pets.id", ondelete="CASCADE"), nullable=False),
    Column("cat_id", PGUUID(as_uuid=True), ForeignKey("categories.id", ondelete="CASCADE"), nullable=False),
    Column("value", Integer, nullable=False),
    Column("note", String(1000), nullable=True),
    Column("time", Double(), nullable=False),
    Column("created_at", Double(), nullable=False, default=lambda: time()),
    Index("idx_states_pet_id_cat_id_time", "pet_id", "cat_id", "time"),
)
events = Table(
    "events",
    metadata,
    Column("id", PGUUID(as_uuid=True), primary_key=True, default=uuid.uuid4),
    Column("pet_id", PGUUID(as_uuid=True), ForeignKey("pets.id", ondelete="CASCADE"), nullable=False),
    Column("name", String(255), nullable=False),
    Column("type", str_enum(EventType, "event_type", length=30), nullable=False),
    Column("status", str_enum(EventStatus, "event_status"), nullable=False),
    Column("schedule", Double(), nullable=False),
    Column("period", str_enum(EventPeriod, "event_period"), nullable=False),
    Column("description", String(2000), nullable=True),
    Column("done_at", Double(), nullable=True),
    Column("created_at", Double(), nullable=False, default=lambda: time()),
    Column("updated_at", Double(), nullable=False, default=lambda: time()),
    Index("idx_events_pet_id", "pet_id"),
    Index("idx_events_status_schedule", "status", "schedule"),
)
notifications = Table(
    "notifications",
    metadata,
    Column("id", PGUUID(as_uuid=True), primary_key=True, default=uuid.uuid4),
    Column("event_id", PGUUID(as_uuid=True), ForeignKey("events.id", ondelete="CASCADE"), nullable=False),
    Column("type", str_enum(NotificationType, "notification_type"), nullable=False),
    Column("status", str_enum(NotificationStatus, "notification_status"), nullable=False),
    Column("time", Double(), nullable=False),
    Column("created_at", Double(), nullable=False, default=lambda: time()),
    Index("idx_notifications_event_id", "event_id"),
    Index("idx_notifications_status_time", "status", "time"),
)
notes = Table(
    "notes",
    metadata,
    Column("id", PGUUID(as_uuid=True), primary_key=True, default=uuid.uuid4),
    Column("pet_id", PGUUID(as_uuid=True), ForeignKey("pets.id", ondelete="CASCADE"), nullable=False),
    Column("content", String(2000), nullable=False),
    Column("created_at", Double(), nullable=False, default=lambda: time()),
    Column("updated_at", Double(), nullable=False, default=lambda: time()),
    Index("idx_notes_pet_id", "pet_id"),
)
food = Table(
    "food",
    metadata,
    Column("id", PGUUID(as_uuid=True), primary_key=True, default=uuid.uuid4),
    Column("pet_id", PGUUID(as_uuid=True), ForeignKey("pets.id", ondelete="CASCADE"), nullable=False),
    Column("name", String(255), nullable=False),
    Column("weight", Integer, nullable=True),
    Column("ingredients", JSON().with_variant(JSONB(), "postgresql"), nullable=False, default=list),
    Column("is_approach", Boolean, nullable=True),
    Column("is_tolerability", Boolean, nullable=True),
    Column("consequences", String(1000), nullable=True),
    Column("created_at", Double(), nullable=False, default=lambda: time()),
    Column("updated_at", Double(), nullable=False, default=lambda: time()),
    Index("idx_food_pet_id_created_at", "pet_id", "created_at"),
)
refresh_tokens = Table(
    "refresh_tokens",
    metadata,
    Column("id", PGUUID(as_uuid=True), primary_key=True, default=uuid.uuid4),
    Column("user_id", PGUUID(as_uuid=True), ForeignKey("users.id"), nullable=False),
    Column("hashed_token", String(255), nullable=False),
    Column("expires_at", Double(), nullable=False),
    Column("created_at", Double(), nullable=False, default=lambda: time()),
    Index("idx_refresh_tokens_user_id", "user_id"),
    Index("idx_refresh_tokens_hashed_token", "hashed_token"),
)


def start_mappers() -> None:
    """Configure once; both ASGI startup and Alembic use this metadata."""
    if list(mapper_registry.mappers):
        return
    mapper_registry.map_imperatively(User, users)
    mapper_registry.map_imperatively(Animal, animals)
    mapper_registry.map_imperatively(
        Breed, breeds, properties={"animal": relationship(Animal, lazy="selectin", viewonly=True)}
    )
    mapper_registry.map_imperatively(
        Pet, pets, properties={"breed": relationship(Breed, lazy="selectin", viewonly=True)}
    )
    mapper_registry.map_imperatively(Category, categories)
    mapper_registry.map_imperatively(State, states)
    mapper_registry.map_imperatively(Event, events)
    mapper_registry.map_imperatively(
        Notification, notifications, properties={"event": relationship(Event, lazy="selectin")}
    )
    mapper_registry.map_imperatively(Note, notes)
    mapper_registry.map_imperatively(Food, food)
    mapper_registry.map_imperatively(RefreshToken, refresh_tokens, properties={"user": relationship(User)})


start_mappers()
