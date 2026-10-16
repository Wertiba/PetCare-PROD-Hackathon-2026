from enum import Enum


class UserRole(str, Enum):
    USER = "USER"
    ADMIN = "ADMIN"


class PetType(str, Enum):
    CAT = "cat"
    DOG = "dog"
    RODENT = "rodent"
    BIRD = "bird"
    REPTILE = "reptile"
    OTHER = "other"
