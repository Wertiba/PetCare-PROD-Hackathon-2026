from enum import Enum


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
