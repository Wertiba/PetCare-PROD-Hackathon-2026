from app.domain.errors import EntityError


class UserNotFoundError(EntityError):
    pass


class ForbiddenError(EntityError):
    pass


class InvalidPasswordError(EntityError):
    pass


class UserAlreadyExistsError(EntityError):
    def __init__(self, login: str):
        super().__init__(login)
        self.login = login


class InvalidCredentialsError(EntityError):
    pass


class WrongLoginOrPasswordError(InvalidCredentialsError):
    """Login failed; kept apart from a bad token so the client can tell the user what is wrong."""


class UserNotActiveError(EntityError):
    pass
