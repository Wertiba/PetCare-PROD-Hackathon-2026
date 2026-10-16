from uuid import UUID

from app.core.exceptions.user_exs import UserNotFoundError
from app.core.schemas.user import UserReadResponse, UserUpdateBody
from app.infrastructure.models import User
from app.infrastructure.unit_of_work import UnitOfWork


class UserService:
    def __init__(self, uow: UnitOfWork):
        self.uow = uow

    @staticmethod
    def _to_read_response(user: User) -> UserReadResponse:
        return UserReadResponse(
            id=user.id,
            email=user.email,
            fullName=user.full_name,
            role=user.role,
            isActive=user.is_active,
            createdAt=user.created_at,
            updatedAt=user.updated_at,
            createdBy=user.created_by,
        )

    async def get_me(self, user_id: UUID) -> UserReadResponse:
        async with self.uow:
            user = await self.uow.user_repo.get_by_id(user_id)
            if user is None:
                raise UserNotFoundError
            return self._to_read_response(user)

    async def update_me(self, user_id: UUID, data: UserUpdateBody) -> UserReadResponse:
        async with self.uow:
            user = await self.uow.user_repo.update(user_id, {"full_name": data.fullName})
            if user is None:
                raise UserNotFoundError
            return self._to_read_response(user)
