from datetime import UTC, datetime

from pydantic import BaseModel, ConfigDict, field_validator

# Postgres INTEGER columns: larger values fail in the driver instead of the request validation.
INT32_MAX = 2**31 - 1
# For text query parameters: Postgres text cannot hold NUL.
NO_NUL_PATTERN = r"^[^\x00]*$"


def validate_timestamp(value: float) -> float:
    try:
        datetime.fromtimestamp(value, UTC)
    except (OverflowError, OSError, ValueError) as exc:
        raise ValueError("timestamp is outside the supported date range") from exc
    return value


def strip_required_text(value: object) -> object:
    if value is None:
        raise ValueError("value cannot be null")
    if isinstance(value, str):
        return value.strip()
    return value


def strip_optional_text(value: object) -> object:
    if isinstance(value, str):
        stripped = value.strip()
        return stripped or None
    return value


class PyModel(BaseModel):
    model_config = ConfigDict(from_attributes=True, allow_inf_nan=False)

    @field_validator("*")
    @classmethod
    def reject_nul(cls, value: object) -> object:
        # Postgres text cannot hold NUL, so such input would fail in the database with a 500.
        texts = value if isinstance(value, list) else [value]
        if any(isinstance(text, str) and "\x00" in text for text in texts):
            raise ValueError("text must not contain NUL characters")
        return value
