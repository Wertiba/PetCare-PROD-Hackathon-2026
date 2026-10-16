from app.api.v1.exceptions.api_exs import (
    BreedNotFound,
    BreedTypeMismatch,
    CategoryNotFoundRef,
    EmailAlreadyExists,
    EventNotFoundRef,
    EventNotPlanned,
    Forbidden,
    Inactive,
    InvalidStateValue,
    NotFound,
    PayloadTooLarge,
    PetNotFoundRef,
    SystemCategoryReadOnly,
    Unauthorized,
    UnsupportedMedia,
    ValidationFailed,
)
from app.core.exceptions.base import UnprocessableEntityError
from app.core.exceptions.breed_exs import BreedNotFoundError, BreedTypeMismatchError
from app.core.exceptions.category_exs import (
    CategoryNotFoundError,
    RelatedCategoryNotFoundError,
    SystemCategoryReadOnlyError,
)
from app.core.exceptions.event_exs import EventNotFoundError, EventNotPlannedError, RelatedEventNotFoundError
from app.core.exceptions.notification_exs import NotificationNotFoundError
from app.core.exceptions.pet_exs import (
    FileTooLargeError,
    PetNotFoundError,
    RelatedPetNotFoundError,
    UnsupportedFileTypeError,
)
from app.core.exceptions.state_exs import InvalidStateValueError, StateNotFoundError
from app.core.exceptions.user_exs import (
    ForbiddenError,
    InvalidCredentialsError,
    InvalidPasswordError,
    UserAlreadyExistsError,
    UserNotActiveError,
    UserNotFoundError,
)

DOMAIN_TO_API: dict[type, callable] = {
    UserNotFoundError: lambda path, exc=None: NotFound(
        path=path,
        message="User not found",
    ),
    ForbiddenError: lambda path, exc=None: Forbidden(
        path=path,
    ),
    InvalidCredentialsError: lambda path, exc=None: Unauthorized(
        path=path,
    ),
    InvalidPasswordError: lambda path, exc=None: Unauthorized(
        path=path,
    ),
    UserAlreadyExistsError: lambda path, exc: EmailAlreadyExists(
        path=path,
        details={"field": "email", "value": exc.email},
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
    BreedNotFoundError: lambda path, exc=None: BreedNotFound(
        path=path,
        details={"field": "breedId"},
    ),
    BreedTypeMismatchError: lambda path, exc=None: BreedTypeMismatch(
        path=path,
        details={"field": "breedId"},
    ),
    FileTooLargeError: lambda path, exc=None: PayloadTooLarge(
        path=path,
    ),
    UnsupportedFileTypeError: lambda path, exc=None: UnsupportedMedia(
        path=path,
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
        details={"field": "catId"},
    ),
    SystemCategoryReadOnlyError: lambda path, exc=None: SystemCategoryReadOnly(
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
}
