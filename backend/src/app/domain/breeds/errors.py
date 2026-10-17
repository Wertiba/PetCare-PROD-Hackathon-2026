from app.domain.errors import EntityError


class BreedNotFoundError(EntityError):
    pass


class BreedTypeMismatchError(EntityError):
    pass
