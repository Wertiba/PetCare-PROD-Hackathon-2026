from enum import Enum

from sqlalchemy import Enum as SAEnum
from sqlalchemy.orm import DeclarativeBase


class Base(DeclarativeBase):
    pass


def str_enum(enum_cls: type[Enum], name: str, length: int = 20) -> SAEnum:
    """Enum stored as plain VARCHAR with lowercase values, like the rest of the schema."""
    return SAEnum(
        enum_cls,
        name=name,
        native_enum=False,
        length=length,
        values_callable=lambda cls: [member.value for member in cls],
    )
