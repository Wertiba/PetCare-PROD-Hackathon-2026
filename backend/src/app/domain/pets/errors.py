from app.domain.errors import EntityError


class PetNotFoundError(EntityError):
    pass


class RelatedPetNotFoundError(EntityError):
    """petId in a request body points to a pet of another user or to nothing."""


class FileTooLargeError(EntityError):
    pass


class UnsupportedFileTypeError(EntityError):
    pass


class PetPhotoRequiredError(EntityError):
    pass


class GeneratedAvatarMissingError(EntityError):
    pass


class AvatarGenerationFailedError(EntityError):
    pass


class AvatarGenerationUnavailableError(EntityError):
    pass
