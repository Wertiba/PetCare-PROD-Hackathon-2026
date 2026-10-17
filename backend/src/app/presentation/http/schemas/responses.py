from time import time
from typing import Any
from uuid import uuid4

from pydantic import Field

from app.presentation.http.schemas.base import PyModel


class MessageResponse(PyModel):
    message: str


class PingResponse(PyModel):
    status: str = "ok"


class ErrorResponse(PyModel):
    code: str
    message: str
    traceId: str
    timestamp: float = Field(description="Unix seconds in UTC; fractional seconds are supported.")
    path: str
    details: dict[str, Any] | None = None


class FieldError(PyModel):
    field: str
    issue: str
    rejectedValue: Any


class ValidationErrorResponse(PyModel):
    code: str = "VALIDATION_FAILED"
    message: str = "Some fields are not correct."
    traceId: str = Field(default_factory=lambda: str(uuid4()))
    timestamp: float = Field(default_factory=time, description="Unix seconds in UTC; fractional seconds are supported.")
    path: str
    fieldErrors: list[FieldError]
