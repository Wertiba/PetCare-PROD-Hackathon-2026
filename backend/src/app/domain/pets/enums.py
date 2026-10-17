from enum import Enum


class PetType(str, Enum):
    CAT = "cat"
    DOG = "dog"
    RODENT = "rodent"
    BIRD = "bird"
    FISH = "fish"
    REPTILE = "reptile"
    OTHER = "other"
