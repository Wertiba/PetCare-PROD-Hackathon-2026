"""Fold a pet's raw history into the handful of facts and series a report shows.

A year of care can be a thousand records; the owner (or the vet they hand the PDF to) needs what is due,
what was done, how the weight moved and which food did not suit, not the log itself.
"""

from collections import Counter, defaultdict
from collections.abc import Iterable
from datetime import UTC, datetime

from app.application.reports.dto import (
    CheckSummary,
    FoodSummary,
    MeasurementSeries,
    MonthActivity,
    PetReport,
    ProcedureSummary,
    ReportEvent,
    ReportNote,
    ScaleSummary,
)
from app.domain.categories.entity import Category
from app.domain.categories.enums import CategoryType
from app.domain.events.entity import Event
from app.domain.events.enums import EventPeriod, EventStatus, EventType
from app.domain.foods.entity import Food
from app.domain.foods.rules import ingredient_key, suspect_ingredients
from app.domain.notes.entity import Note
from app.domain.pets.entity import Pet
from app.domain.pets.rules import age_months
from app.domain.states.entity import State

UPCOMING_LIMIT = 8
SERIES_LIMIT = 3
NOTES_LIMIT = 8
ACTIVITY_MONTHS = 12
SCALE_WINDOW = 90 * 86400
_TRACKED = (EventType.VACCINATION, EventType.PARASITE_TREATMENT, EventType.MEDICATION, EventType.GROOMING)


def _done_at(event: Event) -> float:
    return event.done_at if event.done_at is not None else event.schedule


def _month_start(moment: float) -> datetime:
    point = datetime.fromtimestamp(moment, UTC)
    return datetime(point.year, point.month, 1, tzinfo=UTC)


def upcoming(events: Iterable[Event], now: float) -> list[ReportEvent]:
    planned = sorted((event for event in events if event.status == EventStatus.PLANNED), key=lambda e: e.schedule)
    return [
        ReportEvent(name=event.name, type=event.type, schedule=event.schedule, is_overdue=event.schedule < now)
        for event in planned[:UPCOMING_LIMIT]
    ]


def procedures(events: Iterable[Event], now: float) -> list[ProcedureSummary]:
    """Repeating care grouped by procedure: how many times done, when last, when next."""
    groups: dict[tuple[EventType, str], list[Event]] = defaultdict(list)
    for event in events:
        if event.type in _TRACKED or event.period != EventPeriod.NONE:
            groups[(event.type, event.name)].append(event)
    result = []
    for (type_, name), group in groups.items():
        done = [_done_at(event) for event in group if event.status == EventStatus.DONE]
        planned = [event.schedule for event in group if event.status == EventStatus.PLANNED]
        next_planned = min(planned) if planned else None
        result.append(
            ProcedureSummary(
                name=name,
                type=type_,
                period=max(group, key=lambda event: event.schedule).period,
                times_done=len(done),
                last_done=max(done) if done else None,
                next_planned=next_planned,
                is_overdue=next_planned is not None and next_planned < now,
            )
        )
    # What needs attention first: overdue and soonest on top, finished courses at the bottom.
    return sorted(result, key=lambda item: (item.next_planned is None, item.next_planned or 0, item.name))


def activity(events: Iterable[Event], now: float) -> list[MonthActivity]:
    """Done procedures per calendar month for the last year, the current month last."""
    current = _month_start(now)
    months = []
    for back in range(ACTIVITY_MONTHS - 1, -1, -1):
        year, month = divmod(current.year * 12 + current.month - 1 - back, 12)
        months.append(datetime(year, month + 1, 1, tzinfo=UTC))
    counts: dict[datetime, Counter] = {month: Counter() for month in months}
    for event in events:
        if event.status == EventStatus.DONE:
            month = _month_start(_done_at(event))
            if month in counts:
                counts[month][event.type] += 1
    return [MonthActivity(month_start=month.timestamp(), done=dict(counts[month])) for month in months]


def measurements(
    states: Iterable[State], categories: dict, now: float
) -> tuple[list[MeasurementSeries], list[ScaleSummary], list[CheckSummary]]:
    by_category: dict = defaultdict(list)
    for state in states:
        if state.category_id in categories:
            by_category[state.category_id].append(state)
    series, scales, checks = [], [], []
    for category_id, records in by_category.items():
        category: Category = categories[category_id]
        records.sort(key=lambda state: state.time)
        if category.type == CategoryType.NUMBER and len(records) >= 2:
            points = [(state.time, state.value) for state in records]
            series.append(MeasurementSeries(name=category.name, unit=category.unit, points=points))
        elif category.type == CategoryType.SCALE:
            recent = [state.value for state in records if state.time >= now - SCALE_WINDOW] or [records[-1].value]
            scales.append(ScaleSummary(name=category.name, average=sum(recent) / len(recent), count=len(recent)))
        elif category.type == CategoryType.CHECK:
            happened = [state for state in records if state.value]
            if happened:
                checks.append(CheckSummary(name=category.name, count=len(happened), last=happened[-1].time))
    # Long series first: weight measured monthly beats a parameter written down twice.
    series.sort(key=lambda item: (-len(item.points), item.name))
    return series[:SERIES_LIMIT], sorted(scales, key=lambda s: s.name), sorted(checks, key=lambda c: -c.count)


def foods(records: Iterable[Food]) -> tuple[list[FoodSummary], dict[str, int], list[str]]:
    """Per-food verdicts, the overall suited/unsuited split and the ingredients to suspect."""
    records = sorted(records, key=lambda food: food.created_at)
    groups: dict[str, list[Food]] = defaultdict(list)
    for food in records:
        groups[food.name].append(food)
    summaries = [
        FoodSummary(
            name=name,
            times=len(group),
            liked=sum(food.is_approach is True for food in group),
            disliked=sum(food.is_approach is False for food in group),
            suited=sum(food.is_tolerability is True for food in group),
            unsuited=sum(food.is_tolerability is False for food in group),
            reactions=list(dict.fromkeys(food.consequences for food in group if food.consequences)),
        )
        for name, group in groups.items()
    ]
    summaries.sort(key=lambda item: (-item.unsuited, -item.times, item.name))
    tolerance = {
        "suited": sum(food.is_tolerability is True for food in records),
        "unsuited": sum(food.is_tolerability is False for food in records),
        "unknown": sum(food.is_tolerability is None for food in records),
    }
    tolerated = [food.ingredients for food in records if food.is_tolerability is True]
    suspects: dict[str, str] = {}
    for food in records:
        if food.is_tolerability is False:
            for ingredient in suspect_ingredients(food.ingredients, tolerated):
                suspects.setdefault(ingredient_key(ingredient), ingredient)
    return summaries, tolerance, list(suspects.values())


def report_notes(events: Iterable[Event], notes: Iterable[Note]) -> list[ReportNote]:
    """Vet conclusions and the owner's notes, newest first."""
    items = [
        ReportNote(moment=_done_at(event), title=event.name, text=event.description)
        for event in events
        if event.type == EventType.VET_VISIT and event.status == EventStatus.DONE and event.description
    ]
    items += [ReportNote(moment=note.created_at, title="Заметка", text=note.content) for note in notes]
    return sorted(items, key=lambda item: -item.moment)[:NOTES_LIMIT]


def build_report(
    pet: Pet,
    *,
    events: list[Event],
    states: list[State],
    categories: dict,
    food_records: list[Food],
    notes: list[Note],
    photo: bytes | None,
    now: float,
) -> PetReport:
    breed = pet.breed
    series, scales, checks = measurements(states, categories, now)
    food_summaries, tolerance, suspects = foods(food_records)
    upcoming_events = upcoming(events, now)
    return PetReport(
        pet_name=pet.name,
        animal=breed.animal.name if breed is not None and breed.animal is not None else None,
        breed=breed.name if breed is not None else None,
        birth_date=pet.birth_date,
        age_months=age_months(pet.birth_date, datetime.fromtimestamp(now, UTC).date()),
        photo=photo,
        generated_at=now,
        done_by_type=dict(Counter(event.type for event in events if event.status == EventStatus.DONE)),
        feedings=len(food_records),
        upcoming=upcoming_events,
        overdue=sum(event.status == EventStatus.PLANNED and event.schedule < now for event in events),
        procedures=procedures(events, now),
        activity=activity(events, now),
        series=series,
        scales=scales,
        checks=checks,
        foods=food_summaries,
        tolerance=tolerance,
        suspects=suspects,
        notes=report_notes(events, notes),
    )
