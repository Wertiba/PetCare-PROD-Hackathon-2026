from pydantic import Field

from app.presentation.http.schemas.base import PyModel


class Token(PyModel):
    accessToken: str
    expiresIn: int


class AccessTokenResponse(PyModel):
    accessToken: str = Field(
        deprecated=True,
        description=(
            "Deprecated: retained in the response body for backward compatibility and will be removed in a future "
            "API version. Use the HttpOnly accessToken cookie instead. No removal date has been scheduled."
        ),
    )
    expiresIn: int
