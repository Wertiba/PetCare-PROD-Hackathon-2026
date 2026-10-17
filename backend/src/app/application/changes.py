from time import time
from typing import Any


def apply_changes[T](entity: T, changes: dict[str, Any]) -> T:
    for name, value in changes.items():
        setattr(entity, name, value)
    if hasattr(entity, "updated_at"):
        entity.updated_at = time()
    return entity
