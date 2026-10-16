from .api_exs import (
    BadRequest,
    BreedNotFound,
    BreedTypeMismatch,
    EmailAlreadyExists,
    Forbidden,
    Inactive,
    NotFound,
    PayloadTooLarge,
    Unauthorized,
    UnsupportedMedia,
    ValidationFailed,
)
from .base import APIException

__all__ = [
    "APIException",
    "BadRequest",
    "BreedNotFound",
    "BreedTypeMismatch",
    "EmailAlreadyExists",
    "Forbidden",
    "Inactive",
    "NotFound",
    "PayloadTooLarge",
    "Unauthorized",
    "UnsupportedMedia",
    "ValidationFailed",
]
