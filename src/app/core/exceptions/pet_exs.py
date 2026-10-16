from app.core.exceptions.base import EntityError


class PetNotFoundError(EntityError):
    pass


class FileTooLargeError(EntityError):
    pass


class UnsupportedFileTypeError(EntityError):
    pass
