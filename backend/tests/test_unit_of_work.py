from datetime import UTC, datetime, timedelta
import pytest
from sqlalchemy import func, select
from app.domain.refresh_tokens.entity import RefreshToken
from app.domain.users.entity import User
from app.domain.users.enums import UserRole
from app.application.exceptions import DuplicateError
from app.infra.database.unit_of_work import SqlAlchemyUnitOfWork
from app.infra.gateways.refresh_token import SqlAlchemyRefreshTokenGateway
from app.infra.gateways.user import SqlAlchemyUserGateway


def make_user(login="user"):
    return User(login=login, password="hashed", full_name="Test User", role=UserRole.USER)


async def test_add_query_tracked_update_and_delete(db_session_factory):
    async with db_session_factory() as session:
        user = make_user()
        token = RefreshToken(
            user_id=user.id, hashed_token="abc123", expires_at=(datetime.now(UTC) + timedelta(days=30)).timestamp()
        )
        token.user = user
        uow = SqlAlchemyUnitOfWork(session)
        await uow.add(user)
        await uow.add(token)
        await uow.commit()
    async with db_session_factory() as session:
        user = await SqlAlchemyUserGateway(session).get_by_login("user")
        assert user is not None
        user.full_name = "Updated User"
        token = await SqlAlchemyRefreshTokenGateway(session).get_by_user_and_hash(user.id, "abc123")
        assert token is not None
        uow = SqlAlchemyUnitOfWork(session)
        await uow.delete(token)
        await uow.commit()
    async with db_session_factory() as session:
        found = await SqlAlchemyUserGateway(session).get_by_login("user")
        assert found.full_name == "Updated User"
        assert await SqlAlchemyRefreshTokenGateway(session).get_by_hash("abc123") is None


async def test_uncommitted_changes_are_discarded(db_session_factory):
    async with db_session_factory() as session:
        user = make_user()
        await SqlAlchemyUnitOfWork(session).add(user)
        await session.flush()
    async with db_session_factory() as session:
        assert await SqlAlchemyUserGateway(session).get_by_id(user.id) is None


async def test_failed_commit_rolls_back_the_entire_write(db_session_factory):
    async with db_session_factory() as session:
        session.add(make_user())
        await session.commit()
    async with db_session_factory() as session:
        uow = SqlAlchemyUnitOfWork(session)
        await uow.add(make_user("another"))
        await uow.add(make_user())
        with pytest.raises(DuplicateError):
            await uow.commit()
        await session.rollback()
    async with db_session_factory() as session:
        assert await session.scalar(select(func.count()).select_from(User)) == 1
