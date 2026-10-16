from datetime import datetime
from typing import Annotated

from pydantic import AfterValidator, BaseModel, ConfigDict, field_serializer

from app.core.utils import as_aware_utc

# Incoming timestamps: naive values are treated as UTC, aware ones are converted to UTC.
UtcDatetime = Annotated[datetime, AfterValidator(as_aware_utc)]


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


def format_iso_z(dt: datetime) -> str:
    """2026-10-17T09:30:00Z, or 2026-10-17T09:30:00.123Z when there is a fractional part."""
    utc_dt = as_aware_utc(dt)
    timespec = "milliseconds" if utc_dt.microsecond else "seconds"
    return utc_dt.isoformat(timespec=timespec).replace("+00:00", "Z")


class PyModel(BaseModel):
    model_config = ConfigDict(from_attributes=True)


class DatetimeResponse(PyModel):
    @field_serializer("createdAt", "updatedAt", check_fields=False)
    def serialize_dt(self, dt: datetime, _info) -> str:
        return format_iso_z(dt)


class TimestampsResponse(DatetimeResponse):
    """Also renders the domain timestamps (time, schedule, doneAt...) as ISO-8601 with a Z suffix."""

    @field_serializer("time", "schedule", "doneAt", "nextSchedule", "from_", "to", check_fields=False)
    def serialize_optional_dt(self, dt: datetime | None, _info) -> str | None:
        if dt is None:
            return None
        return format_iso_z(dt)
