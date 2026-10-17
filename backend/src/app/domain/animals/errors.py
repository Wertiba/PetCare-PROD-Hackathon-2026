from app.domain.errors import EntityError


class AnimalNotFoundError(EntityError):
    pass


class RelatedAnimalNotFoundError(EntityError):
    """animalId in a request body points to nothing."""
