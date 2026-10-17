from enum import Enum


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
