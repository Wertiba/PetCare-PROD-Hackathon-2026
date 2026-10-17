from datetime import UTC, date, datetime


def age_months(birth_timestamp: float | None, today: date | None = None) -> int | None:
    if birth_timestamp is None:
        return None
    birth_date = datetime.fromtimestamp(birth_timestamp, UTC).date()
    today = today or datetime.now(UTC).date()
    months = (today.year - birth_date.year) * 12 + today.month - birth_date.month
    if today.day < birth_date.day:
        months -= 1
    return max(months, 0)
