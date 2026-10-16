from app.core.exceptions.base import EntityError


class BreedNotFoundError(EntityError):
    pass


class BreedTypeMismatchError(EntityError):
    pass
