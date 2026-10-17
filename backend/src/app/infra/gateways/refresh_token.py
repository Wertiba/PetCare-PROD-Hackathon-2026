from sqlalchemy import select
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.ext.asyncio import AsyncSession

from app.application.exceptions import ApplicationError
from app.application.ports.refresh_token_gateway import RefreshTokenGateway
from app.domain.refresh_tokens.entity import RefreshToken
from app.domain.refresh_tokens.ids import RefreshTokenId
from app.domain.users.ids import UserId


class SqlAlchemyRefreshTokenGateway(RefreshTokenGateway):
    def __init__(self, session: AsyncSession) -> None:
        self.session = session

    async def get_by_id(self, id_: RefreshTokenId) -> RefreshToken | None:
        stmt = select(RefreshToken).where(RefreshToken.id == id_)
        try:
            result = await self.session.execute(stmt)
            return result.scalar_one_or_none()
        except SQLAlchemyError as exc:
            raise ApplicationError("Database error") from exc

    async def get_by_user_and_hash(self, user_id: UserId, hashed_token: str) -> RefreshToken | None:
        stmt = select(RefreshToken).where(RefreshToken.user_id == user_id, RefreshToken.hashed_token == hashed_token)
        try:
            result = await self.session.execute(stmt)
            return result.scalar_one_or_none()
        except SQLAlchemyError as e:
            raise ApplicationError("Database error") from e

    async def get_by_hash(self, hashed_token: str) -> RefreshToken | None:
        try:
            result = await self.session.execute(select(RefreshToken).where(RefreshToken.hashed_token == hashed_token))
            return result.scalar_one_or_none()
        except SQLAlchemyError as exc:
            raise ApplicationError("Database error") from exc
