from app.domain.errors import EntityError


class BreedNotFoundError(EntityError):
    pass


class RelatedBreedNotFoundError(EntityError):
    """breedId in a request body points to nothing."""
