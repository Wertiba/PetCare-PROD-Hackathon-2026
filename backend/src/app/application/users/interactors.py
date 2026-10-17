from dataclasses import dataclass

from app.application.changes import apply_changes
from app.application.ports.unit_of_work import UnitOfWork
from app.application.ports.user_gateway import UserGateway
from app.application.users.dto import UserResult, UserUpdateData
from app.domain.users.entity import User
from app.domain.users.errors import UserNotFoundError
from app.domain.users.ids import UserId


@dataclass
class _UserContext:
    uow: UnitOfWork
    user_gateway: UserGateway

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


class GetMe(_UserContext):
    async def __call__(self, user_id: UserId) -> UserResult:
        user = await self.user_gateway.get_by_id(user_id)
        if user is None:
            raise UserNotFoundError
        return self._to_read_response(user)


class UpdateMe(_UserContext):
    async def __call__(self, user_id: UserId, data: UserUpdateData) -> UserResult:
        user = await self.user_gateway.get_by_id(user_id)
        if user is None:
            raise UserNotFoundError
        apply_changes(user, {"full_name": data.changes["fullName"]})
        result = self._to_read_response(user)
        await self.uow.commit()
        return result
