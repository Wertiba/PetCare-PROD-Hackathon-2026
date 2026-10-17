from app.domain.events.entity import Event
from app.domain.events.periods import next_occurrence


def next_schedule_for(event: Event) -> float | None:
    base = event.schedule
    if event.done_at is not None:
        base = max(base, event.done_at)
    return next_occurrence(base, event.period)
