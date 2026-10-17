from dataclasses import dataclass
from time import time
from uuid import UUID

from app.application.auth.dto import AccessTokenResult
from app.application.changes import apply_changes
from app.application.exceptions import DuplicateError
from app.application.ports.refresh_token_gateway import RefreshTokenGateway
from app.application.ports.tokens import ACCESS_TOKEN_TYPE, REFRESH_TOKEN_TYPE, TokenService
from app.application.ports.unit_of_work import UnitOfWork
from app.application.ports.user_gateway import UserGateway
from app.application.users.dto import UserAndAccessTokenResult, UserData, UserLoginData, UserRegisterData, UserResult
from app.domain.refresh_tokens.entity import RefreshToken
from app.domain.users.entity import User
from app.domain.users.enums import UserRole
from app.domain.users.errors import (
    InvalidCredentialsError,
    UserAlreadyExistsError,
    UserNotActiveError,
    WrongLoginOrPasswordError,
)
from app.domain.users.ids import UserId


@dataclass
class _AuthContext:
    uow: UnitOfWork
    user_gateway: UserGateway
    refresh_token_gateway: RefreshTokenGateway
    jwt_service: TokenService

    @staticmethod
    def _to_read_response(user: User) -> UserResult:
        return UserResult(
            id=user.id,
            login=user.login,
            fullName=user.full_name,
            role=user.role,
            isActive=user.is_active,
            createdAt=user.created_at,
            updatedAt=user.updated_at,
            createdBy=user.created_by,
        )

    async def _authenticate_user(self, login: str, password: str) -> User:
        user = await self.user_gateway.get_by_login(login)
        if user is None:
            self.jwt_service.verify_dummy_password(password)
            raise WrongLoginOrPasswordError
        if not self.jwt_service.verify_password(password, str(user.password)):
            raise WrongLoginOrPasswordError
        if not user.is_active:
            raise UserNotActiveError
        return user

    async def _issue_token_pair(self, user: User) -> tuple[UserAndAccessTokenResult, str, int]:
        access_token = self.jwt_service.create_access_token(str(user.id))
        refresh_token = self.jwt_service.create_refresh_token(str(user.id))
        max_age = self.jwt_service.refresh_expire_seconds
        token = RefreshToken(
            user_id=user.id, hashed_token=self.jwt_service.hash_token(refresh_token), expires_at=time() + max_age
        )
        token.user = user
        await self.uow.add(token)
        response = UserAndAccessTokenResult(
            accessToken=access_token,
            expiresIn=self.jwt_service.access_expire_seconds,
            user=self._to_read_response(user),
        )
        return (response, refresh_token, max_age)


class RegisterUser(_AuthContext):
    async def __call__(self, user_data: UserRegisterData) -> tuple[UserAndAccessTokenResult, str, int]:
        existing_user = await self.user_gateway.get_by_login(user_data.login)
        if existing_user:
            raise UserAlreadyExistsError(login=user_data.login)
        hashed_password = self.jwt_service.get_password_hash(user_data.password)
        try:
            user = User(
                login=user_data.login,
                password=hashed_password,
                full_name=user_data.fullName,
                role=UserRole.USER,
                is_active=True,
            )
            await self.uow.add(user)
        except DuplicateError:
            raise UserAlreadyExistsError(login=user_data.login) from None
        user = apply_changes(user, {"created_by": user.id})
        result = await self._issue_token_pair(user)
        try:
            await self.uow.commit()
        except DuplicateError:
            raise UserAlreadyExistsError(login=user_data.login) from None
        return result


class LoginUser(_AuthContext):
    async def __call__(self, login_body: UserLoginData) -> tuple[UserAndAccessTokenResult, str, int]:
        user = await self._authenticate_user(login_body.login, login_body.password)
        result = await self._issue_token_pair(user)
        await self.uow.commit()
        return result


class RefreshTokens(_AuthContext):
    async def __call__(self, raw_refresh_token: str) -> tuple[AccessTokenResult, str, int]:
        payload = self.jwt_service.decode_token(raw_refresh_token, expected_type=REFRESH_TOKEN_TYPE)
        user_id: UserId = UUID(payload["sub"])
        hashed = self.jwt_service.hash_token(raw_refresh_token)
        stored = await self.refresh_token_gateway.get_by_user_and_hash(user_id, hashed)
        if stored is None or stored.expires_at < time():
            raise InvalidCredentialsError
        user = await self.user_gateway.get_by_id(user_id)
        if user is None or not user.is_active:
            raise InvalidCredentialsError
        await self.uow.delete(stored)
        new_access_token = self.jwt_service.create_access_token(str(user.id))
        new_refresh_token = self.jwt_service.create_refresh_token(str(user.id))
        max_age = self.jwt_service.refresh_expire_seconds
        token = RefreshToken(
            user_id=user.id, hashed_token=self.jwt_service.hash_token(new_refresh_token), expires_at=time() + max_age
        )
        token.user = user
        await self.uow.add(token)
        response = AccessTokenResult(accessToken=new_access_token, expiresIn=self.jwt_service.access_expire_seconds)
        result = (response, new_refresh_token, max_age)
        await self.uow.commit()
        return result


class Logout(_AuthContext):
    async def __call__(self, raw_refresh_token: str) -> None:
        hashed = self.jwt_service.hash_token(raw_refresh_token)
        stored = await self.refresh_token_gateway.get_by_hash(hashed)
        if stored is not None:
            await self.uow.delete(stored)
        await self.uow.commit()


class VerifyAccessToken(_AuthContext):
    async def __call__(self, access_token: str) -> UserData:
        payload = self.jwt_service.decode_token(access_token, expected_type=ACCESS_TOKEN_TYPE)
        user_id: UserId = UUID(payload["sub"])
        user = await self.user_gateway.get_by_id(user_id)
        if not user or not user.is_active:
            raise InvalidCredentialsError
        return UserData(
            id=user.id,
            login=user.login,
            fullName=user.full_name,
            role=user.role,
            isActive=user.is_active,
            createdAt=user.created_at,
            updatedAt=user.updated_at,
            createdBy=user.created_by,
        )
