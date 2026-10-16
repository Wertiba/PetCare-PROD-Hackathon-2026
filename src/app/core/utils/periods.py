from datetime import datetime

from dateutil.relativedelta import relativedelta

from app.core.enums import EventPeriod

_PERIOD_STEPS: dict[EventPeriod, relativedelta] = {
    EventPeriod.DAILY: relativedelta(days=1),
    EventPeriod.WEEKLY: relativedelta(weeks=1),
    EventPeriod.MONTHLY: relativedelta(months=1),
    EventPeriod.QUARTERLY: relativedelta(months=3),
    EventPeriod.HALF_YEAR: relativedelta(months=6),
    EventPeriod.YEARLY: relativedelta(years=1),
}


def next_occurrence(base: datetime, period: EventPeriod) -> datetime | None:
    """Date of the next repetition after `base`, or None for a one-off event.

    Month-based steps clamp to the end of month (Jan 31 + 1 month = Feb 28/29).
    """
    step = _PERIOD_STEPS.get(period)
    if step is None:
        return None
    return base + step
