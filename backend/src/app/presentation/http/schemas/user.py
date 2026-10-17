from typing import Annotated

from pydantic import AfterValidator, Field

from app.domain.users.enums import UserRole
from app.domain.users.ids import UserId
from app.presentation.http.password import check_len_password
from app.presentation.http.schemas.base import PyModel
from app.presentation.http.schemas.token import AccessTokenResponse

__all__ = ["UserRole"]


class UserRegisterBody(PyModel):
    login: Annotated[str, Field(min_length=1, max_length=255)]
    password: Annotated[str, AfterValidator(check_len_password)]
    fullName: Annotated[str, Field(pattern="^[а-яА-Яa-zA-Z0-9 _-]{2,200}$")]


class UserUpdateBody(PyModel):
    fullName: Annotated[str, Field(pattern="^[а-яА-Яa-zA-Z0-9 _-]{2,200}$")]


class UserLoginBody(PyModel):
    login: Annotated[str, Field(min_length=1, max_length=255)]
    password: str


class UserData(PyModel):
    id: UserId
    login: str
    fullName: str
    role: UserRole
    isActive: bool
    createdAt: float = Field(description="Unix seconds in UTC; fractional seconds are supported.")
    updatedAt: float = Field(description="Unix seconds in UTC; fractional seconds are supported.")
    createdBy: UserId


class UserReadResponse(UserData):
    pass


class UserAndAccessTokenResponse(AccessTokenResponse):
    user: UserReadResponse
