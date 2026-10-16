from app.core.exceptions.base import EntityError


class EventNotFoundError(EntityError):
    pass


class RelatedEventNotFoundError(EntityError):
    """eventId in a request body points to an event of another user or to nothing."""


class EventNotPlannedError(EntityError):
    pass
