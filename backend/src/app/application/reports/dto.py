from dataclasses import dataclass, field

from app.domain.categories.enums import CategoryUnit
from app.domain.events.enums import EventPeriod, EventType


@dataclass(kw_only=True)
class ReportEvent:
    name: str
    type: EventType
    schedule: float
    is_overdue: bool


@dataclass(kw_only=True)
class ProcedureSummary:
    """One repeating procedure (a vaccine, a flea treatment...) folded from all its occurrences."""

    name: str
    type: EventType
    period: EventPeriod
    times_done: int
    last_done: float | None
    next_planned: float | None
    is_overdue: bool


@dataclass(kw_only=True)
class MonthActivity:
    month_start: float
    done: dict[EventType, int]


@dataclass(kw_only=True)
class MeasurementSeries:
    name: str
    unit: CategoryUnit
    points: list[tuple[float, int]]


@dataclass(kw_only=True)
class ScaleSummary:
    name: str
    average: float
    count: int


@dataclass(kw_only=True)
class CheckSummary:
    """A yes/no observation (stomach upset, allergic reaction...) and how often it happened."""

    name: str
    count: int
    last: float


@dataclass(kw_only=True)
class FoodSummary:
    name: str
    times: int
    liked: int
    disliked: int
    suited: int
    unsuited: int
    reactions: list[str]


@dataclass(kw_only=True)
class ReportNote:
    moment: float
    title: str
    text: str


@dataclass(kw_only=True)
class PetReport:
    pet_name: str
    animal: str | None
    breed: str | None
    birth_date: float | None
    age_months: int | None
    photo: bytes | None
    generated_at: float
    done_by_type: dict[EventType, int]
    feedings: int
    upcoming: list[ReportEvent]
    overdue: int
    procedures: list[ProcedureSummary]
    activity: list[MonthActivity]
    series: list[MeasurementSeries]
    scales: list[ScaleSummary]
    checks: list[CheckSummary]
    foods: list[FoodSummary]
    tolerance: dict[str, int] = field(default_factory=dict)
    suspects: list[str] = field(default_factory=list)
    notes: list[ReportNote] = field(default_factory=list)


@dataclass(kw_only=True)
class PetReportFile:
    filename: str
    content: bytes
