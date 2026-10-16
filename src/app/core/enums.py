from enum import Enum


class UserRole(str, Enum):
    USER = "USER"
    ADMIN = "ADMIN"


class PetType(str, Enum):
    CAT = "cat"
    DOG = "dog"
    RODENT = "rodent"
    BIRD = "bird"
    FISH = "fish"
    REPTILE = "reptile"
    OTHER = "other"


class CategoryKind(str, Enum):
    """How states of a category are aggregated over a period."""

    SUM = "sum"
    AVG = "avg"
    LAST = "last"
    COUNT = "count"
    MIN = "min"
    MAX = "max"


class CategoryType(str, Enum):
    """What a single state value means: 0/1 flag, any number or 1..5 score."""

    CHECK = "check"
    NUMBER = "number"
    SCALE = "scale"


class CategoryUnit(str, Enum):
    NONE = "none"
    G = "g"
    ML = "ml"
    MIN = "min"
    M = "m"
    TIMES = "times"
    RUB = "rub"
    POINTS = "points"


class EventType(str, Enum):
    VACCINATION = "vaccination"
    PARASITE_TREATMENT = "parasite_treatment"
    VET_VISIT = "vet_visit"
    MEDICATION = "medication"
    GROOMING = "grooming"
    OTHER = "other"


class EventStatus(str, Enum):
    PLANNED = "planned"
    DONE = "done"
    SKIPPED = "skipped"
    CANCELLED = "cancelled"


class EventPeriod(str, Enum):
    NONE = "none"
    DAILY = "daily"
    WEEKLY = "weekly"
    MONTHLY = "monthly"
    QUARTERLY = "quarterly"
    HALF_YEAR = "half_year"
    YEARLY = "yearly"


class NotificationType(str, Enum):
    APP = "app"
    TELEGRAM = "telegram"
    WEB_PUSH = "web_push"


class NotificationStatus(str, Enum):
    PENDING = "pending"
    SENT = "sent"
    READ = "read"
    FAILED = "failed"
