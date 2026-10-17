from app.domain.categories.enums import CategoryType
from app.domain.states.errors import InvalidStateValueError

SCALE_MIN = 1
SCALE_MAX = 5


def validate_state_value(category_type: CategoryType, value: int) -> None:
    """check is a 0/1 flag, scale is a 1..5 score, number is any non-negative amount."""
    if category_type == CategoryType.CHECK and value not in {0, 1}:
        raise InvalidStateValueError("Value must be 0 or 1 for a check category", value)
    if category_type == CategoryType.SCALE and (not SCALE_MIN <= value <= SCALE_MAX):
        raise InvalidStateValueError(f"Value must be between {SCALE_MIN} and {SCALE_MAX} for a scale category", value)
    if category_type == CategoryType.NUMBER and value < 0:
        raise InvalidStateValueError("Value must not be negative", value)
