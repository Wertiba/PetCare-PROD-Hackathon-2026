from sqlalchemy import select
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.ext.asyncio import AsyncSession

from app.application.exceptions import ApplicationError
from app.application.ports.user_gateway import UserGateway
from app.domain.users.entity import User
from app.domain.users.ids import UserId


class SqlAlchemyUserGateway(UserGateway):
    def __init__(self, session: AsyncSession) -> None:
        self.session = session

    async def get_by_id(self, id_: UserId) -> User | None:
        stmt = select(User).where(User.id == id_)
        try:
            result = await self.session.execute(stmt)
            return result.scalar_one_or_none()
        except SQLAlchemyError as exc:
            raise ApplicationError("Database error") from exc

    async def get_by_login(self, login: str) -> User | None:
        stmt = select(User).where(User.login == login)
        try:
            result = await self.session.execute(stmt)
            return result.scalar_one_or_none()
        except SQLAlchemyError as e:
            raise ApplicationError("Database error") from e
