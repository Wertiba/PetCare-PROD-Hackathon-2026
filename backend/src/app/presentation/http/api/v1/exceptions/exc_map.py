from app.domain.animals.errors import AnimalNotFoundError, RelatedAnimalNotFoundError
from app.domain.breeds.errors import BreedNotFoundError, RelatedBreedNotFoundError
from app.domain.categories.errors import (
    CategoryInUseError,
    CategoryNotFoundError,
    RelatedCategoryNotFoundError,
    SystemCategoryReadOnlyError,
)
from app.domain.errors import UnprocessableEntityError
from app.domain.events.errors import EventNotFoundError, EventNotPlannedError, RelatedEventNotFoundError
from app.domain.foods.errors import FoodNotFoundError
from app.domain.notes.errors import NoteNotFoundError
from app.domain.notifications.errors import (
    NotificationNotFoundError,
    WebPushEndpointNotAllowedError,
    WebPushEndpointRequiredError,
    WebPushNotConfiguredError,
)
from app.domain.pets.errors import (
    AvatarGenerationFailedError,
    AvatarGenerationUnavailableError,
    AvatarPromptRejectedError,
    FileTooLargeError,
    GeneratedAvatarMissingError,
    PetNotFoundError,
    PetPhotoRequiredError,
    PhotoUploadNotFoundError,
    RelatedPetNotFoundError,
    UnsupportedFileTypeError,
)
from app.domain.states.errors import InvalidStateValueError, StateNotFoundError
from app.domain.users.errors import (
    ForbiddenError,
    InvalidCredentialsError,
    InvalidPasswordError,
    UserAlreadyExistsError,
    UserNotActiveError,
    UserNotFoundError,
    WrongLoginOrPasswordError,
)
from app.presentation.http.api.v1.exceptions.api_exs import (
    AnimalNotFoundRef,
    AvatarGenerationFailed,
    AvatarGenerationUnavailable,
    AvatarPromptRejected,
    BreedNotFound,
    CategoryInUse,
    CategoryNotFoundRef,
    EventNotFoundRef,
    EventNotPlanned,
    Forbidden,
    GeneratedAvatarMissing,
    Inactive,
    InvalidStateValue,
    LoginAlreadyExists,
    NotFound,
    PayloadTooLarge,
    PetNotFoundRef,
    PetPhotoRequired,
    PhotoUploadNotFound,
    SystemCategoryReadOnly,
    Unauthorized,
    UnsupportedMedia,
    ValidationFailed,
    WebPushNotConfigured,
    WrongLoginOrPassword,
)

DOMAIN_TO_API: dict[type, callable] = {
    UserNotFoundError: lambda path, exc=None: NotFound(
        path=path,
        message="User not found",
    ),
    ForbiddenError: lambda path, exc=None: Forbidden(
        path=path,
    ),
    # Before InvalidCredentialsError: the first isinstance match wins.
    WrongLoginOrPasswordError: lambda path, exc=None: WrongLoginOrPassword(
        path=path,
    ),
    InvalidCredentialsError: lambda path, exc=None: Unauthorized(
        path=path,
    ),
    InvalidPasswordError: lambda path, exc=None: Unauthorized(
        path=path,
    ),
    UserAlreadyExistsError: lambda path, exc: LoginAlreadyExists(
        path=path,
        details={"field": "login", "value": exc.login},
    ),
    UnprocessableEntityError: lambda path, exc=None: ValidationFailed(
        path=path,
    ),
    UserNotActiveError: lambda path, exc=None: Inactive(
        path=path,
    ),
    PetNotFoundError: lambda path, exc=None: NotFound(
        path=path,
        message="Pet not found",
    ),
    AnimalNotFoundError: lambda path, exc=None: NotFound(
        path=path,
        message="Animal not found",
    ),
    RelatedAnimalNotFoundError: lambda path, exc=None: AnimalNotFoundRef(
        path=path,
        details={"field": "animalId"},
    ),
    BreedNotFoundError: lambda path, exc=None: NotFound(
        path=path,
        message="Breed not found",
    ),
    RelatedBreedNotFoundError: lambda path, exc=None: BreedNotFound(
        path=path,
        details={"field": "breedId"},
    ),
    FileTooLargeError: lambda path, exc=None: PayloadTooLarge(
        path=path,
    ),
    UnsupportedFileTypeError: lambda path, exc=None: UnsupportedMedia(
        path=path,
    ),
    PetPhotoRequiredError: lambda path, exc=None: PetPhotoRequired(
        path=path,
    ),
    PhotoUploadNotFoundError: lambda path, exc=None: PhotoUploadNotFound(
        path=path,
        details={"field": "key"},
    ),
    GeneratedAvatarMissingError: lambda path, exc=None: GeneratedAvatarMissing(
        path=path,
    ),
    AvatarGenerationFailedError: lambda path, exc=None: AvatarGenerationFailed(
        path=path,
    ),
    AvatarGenerationUnavailableError: lambda path, exc=None: AvatarGenerationUnavailable(
        path=path,
    ),
    AvatarPromptRejectedError: lambda path, exc=None: AvatarPromptRejected(
        path=path,
        details={"field": "prompt"},
    ),
    RelatedPetNotFoundError: lambda path, exc=None: PetNotFoundRef(
        path=path,
        details={"field": "petId"},
    ),
    CategoryNotFoundError: lambda path, exc=None: NotFound(
        path=path,
        message="Category not found",
    ),
    RelatedCategoryNotFoundError: lambda path, exc=None: CategoryNotFoundRef(
        path=path,
        details={"field": "categoryId"},
    ),
    SystemCategoryReadOnlyError: lambda path, exc=None: SystemCategoryReadOnly(
        path=path,
    ),
    CategoryInUseError: lambda path, exc=None: CategoryInUse(
        path=path,
    ),
    StateNotFoundError: lambda path, exc=None: NotFound(
        path=path,
        message="State not found",
    ),
    InvalidStateValueError: lambda path, exc: InvalidStateValue(
        path=path,
        message=exc.reason,
        details={"field": "value", "value": exc.value},
    ),
    EventNotFoundError: lambda path, exc=None: NotFound(
        path=path,
        message="Event not found",
    ),
    RelatedEventNotFoundError: lambda path, exc=None: EventNotFoundRef(
        path=path,
        details={"field": "eventId"},
    ),
    EventNotPlannedError: lambda path, exc=None: EventNotPlanned(
        path=path,
    ),
    NotificationNotFoundError: lambda path, exc=None: NotFound(
        path=path,
        message="Notification not found",
    ),
    WebPushNotConfiguredError: lambda path, exc=None: WebPushNotConfigured(path=path),
    WebPushEndpointNotAllowedError: lambda path, exc=None: ValidationFailed(
        path=path,
        details={"field": "endpoint"},
    ),
    WebPushEndpointRequiredError: lambda path, exc=None: ValidationFailed(
        path=path,
        details={"field": "endpoint"},
    ),
    NoteNotFoundError: lambda path, exc=None: NotFound(
        path=path,
        message="Note not found",
    ),
    FoodNotFoundError: lambda path, exc=None: NotFound(
        path=path,
        message="Food not found",
    ),
}
