from app.core.exceptions.base import EntityError


class StateNotFoundError(EntityError):
    pass


class InvalidStateValueError(EntityError):
    def __init__(self, reason: str, value: int):
        super().__init__(reason)
        self.reason = reason
        self.value = value
