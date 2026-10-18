from time import time
from typing import Any
from uuid import uuid4

from pydantic import BaseModel, Field

from app.presentation.http.schemas.base import PyModel


class _EchoModel(BaseModel):
    """Error payloads echo the rejected input, so they must not run the PyModel input checks on it."""

    model_config = PyModel.model_config


class MessageResponse(PyModel):
    message: str


class PingResponse(PyModel):
    status: str = "ok"


class ErrorResponse(_EchoModel):
    code: str
    message: str
    traceId: str
    timestamp: float = Field(description="Unix seconds in UTC; fractional seconds are supported.")
    path: str
    details: dict[str, Any] | None = None


class FieldError(_EchoModel):
    field: str
    issue: str
    rejectedValue: Any


class ValidationErrorResponse(_EchoModel):
    code: str = "VALIDATION_FAILED"
    message: str = "Some fields are not correct."
    traceId: str = Field(default_factory=lambda: str(uuid4()))
    timestamp: float = Field(default_factory=time, description="Unix seconds in UTC; fractional seconds are supported.")
    path: str
    fieldErrors: list[FieldError]
