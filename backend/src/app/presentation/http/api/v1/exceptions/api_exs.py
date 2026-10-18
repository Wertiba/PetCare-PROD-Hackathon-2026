from fastapi import status

from app.presentation.http.api.v1.exceptions.base import APIException


class BadRequest(APIException):
    status_code = status.HTTP_400_BAD_REQUEST
    code = "BAD_REQUEST"
    message = "Invalid request"


class Unauthorized(APIException):
    status_code = status.HTTP_401_UNAUTHORIZED
    code = "UNAUTHORIZED"
    message = "The token is missing or invalid"


class WrongLoginOrPassword(APIException):
    status_code = status.HTTP_401_UNAUTHORIZED
    code = "WRONG_LOGIN_OR_PASSWORD"
    message = "Wrong login or password"


class Forbidden(APIException):
    status_code = status.HTTP_403_FORBIDDEN
    code = "FORBIDDEN"
    message = "Insufficient rights to perform the operation"


class NotFound(APIException):
    status_code = status.HTTP_404_NOT_FOUND
    code = "NOT_FOUND"
    message = "Resource not found"


class LoginAlreadyExists(APIException):
    status_code = status.HTTP_409_CONFLICT
    code = "LOGIN_ALREADY_EXISTS"
    message = "User with this login already exists"


class ValidationFailed(APIException):
    status_code = status.HTTP_422_UNPROCESSABLE_CONTENT
    code = "VALIDATION_FAILED"
    message = "Some fields are not correct."


class Inactive(APIException):
    status_code = status.HTTP_423_LOCKED
    code = "USER_INACTIVE"
    message = "The user has been deactivated"


class PayloadTooLarge(APIException):
    status_code = status.HTTP_413_CONTENT_TOO_LARGE
    code = "FILE_TOO_LARGE"
    message = "File is too large"


class UnsupportedMedia(APIException):
    status_code = status.HTTP_415_UNSUPPORTED_MEDIA_TYPE
    code = "UNSUPPORTED_FILE_TYPE"
    message = "Unsupported file type"


class BreedNotFound(APIException):
    status_code = status.HTTP_422_UNPROCESSABLE_CONTENT
    code = "BREED_NOT_FOUND"
    message = "Breed not found"


class AnimalNotFoundRef(APIException):
    status_code = status.HTTP_422_UNPROCESSABLE_CONTENT
    code = "ANIMAL_NOT_FOUND"
    message = "Animal not found"


class Conflict(APIException):
    status_code = status.HTTP_409_CONFLICT
    code = "CONFLICT"
    message = "Resource already exists"


class PetNotFoundRef(APIException):
    status_code = status.HTTP_422_UNPROCESSABLE_CONTENT
    code = "PET_NOT_FOUND"
    message = "Pet not found"


class CategoryNotFoundRef(APIException):
    status_code = status.HTTP_422_UNPROCESSABLE_CONTENT
    code = "CATEGORY_NOT_FOUND"
    message = "Category not found"


class EventNotFoundRef(APIException):
    status_code = status.HTTP_422_UNPROCESSABLE_CONTENT
    code = "EVENT_NOT_FOUND"
    message = "Event not found"


class InvalidStateValue(APIException):
    status_code = status.HTTP_422_UNPROCESSABLE_CONTENT
    code = "INVALID_VALUE"
    message = "Value does not fit the category type"


class SystemCategoryReadOnly(APIException):
    status_code = status.HTTP_403_FORBIDDEN
    code = "SYSTEM_CATEGORY_READ_ONLY"
    message = "Built-in categories cannot be changed or deleted"


class EventNotPlanned(APIException):
    status_code = status.HTTP_409_CONFLICT
    code = "EVENT_NOT_PLANNED"
    message = "Only a planned event can be completed"


class CategoryInUse(APIException):
    status_code = status.HTTP_409_CONFLICT
    code = "CATEGORY_IN_USE"
    message = "Other users record states in this category"


class PetPhotoRequired(APIException):
    status_code = status.HTTP_422_UNPROCESSABLE_CONTENT
    code = "PET_PHOTO_REQUIRED"
    message = "Pet photo is required"


class PhotoUploadNotFound(APIException):
    status_code = status.HTTP_422_UNPROCESSABLE_CONTENT
    code = "PHOTO_UPLOAD_NOT_FOUND"
    message = "Uploaded photo not found"


class GeneratedAvatarMissing(APIException):
    status_code = status.HTTP_422_UNPROCESSABLE_CONTENT
    code = "GENERATED_AVATAR_MISSING"
    message = "Generated avatar is missing"


class AvatarGenerationFailed(APIException):
    status_code = status.HTTP_502_BAD_GATEWAY
    code = "AVATAR_GENERATION_FAILED"
    message = "Avatar generation failed"


class AvatarGenerationUnavailable(APIException):
    status_code = status.HTTP_503_SERVICE_UNAVAILABLE
    code = "AVATAR_GENERATION_UNAVAILABLE"
    message = "Avatar generation is unavailable"


class AvatarPromptRejected(APIException):
    status_code = status.HTTP_422_UNPROCESSABLE_CONTENT
    code = "AVATAR_PROMPT_REJECTED"
    message = "Prompt must be a short description of the avatar look"


class WebPushNotConfigured(APIException):
    status_code = status.HTTP_503_SERVICE_UNAVAILABLE
    code = "WEB_PUSH_NOT_CONFIGURED"
    message = "Web Push is not configured"
