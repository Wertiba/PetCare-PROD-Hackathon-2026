from calendar import monthrange
from datetime import UTC, datetime

from app.domain.events.enums import EventPeriod


def next_occurrence(base: float, period: EventPeriod) -> float | None:
    """Advance Unix seconds in UTC, clamping month-based repeats to the month's last day."""
    if period == EventPeriod.NONE:
        return None
    if period == EventPeriod.DAILY:
        return base + 86400
    if period == EventPeriod.WEEKLY:
        return base + 7 * 86400
    months = {EventPeriod.MONTHLY: 1, EventPeriod.QUARTERLY: 3, EventPeriod.HALF_YEAR: 6, EventPeriod.YEARLY: 12}[
        period
    ]
    original = datetime.fromtimestamp(base, UTC)
    year, month = divmod(original.year * 12 + original.month - 1 + months, 12)
    month += 1
    day = min(original.day, monthrange(year, month)[1])
    return original.replace(year=year, month=month, day=day).timestamp()
