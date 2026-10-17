from dataclasses import dataclass
from typing import Any

from app.domain.users.enums import UserRole
from app.domain.users.ids import UserId


@dataclass(kw_only=True)
class UserRegisterData:
    login: str
    password: str
    fullName: str


@dataclass(kw_only=True)
class UserUpdateData:
    changes: dict[str, Any]


@dataclass(kw_only=True)
class UserLoginData:
    login: str
    password: str


@dataclass(kw_only=True)
class UserData:
    id: UserId
    login: str
    fullName: str
    role: UserRole
    isActive: bool
    createdAt: float
    updatedAt: float
    createdBy: UserId


@dataclass(kw_only=True)
class UserResult:
    id: UserId
    login: str
    fullName: str
    role: UserRole
    isActive: bool
    createdAt: float
    updatedAt: float
    createdBy: UserId


@dataclass(kw_only=True)
class UserAndAccessTokenResult:
    accessToken: str
    expiresIn: int
    user: UserResult
