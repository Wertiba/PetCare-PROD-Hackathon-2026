import pytest
from sqlalchemy.ext.asyncio import async_sessionmaker, create_async_engine
from app.domain.users.errors import InvalidCredentialsError
from app.domain.users.errors import UserAlreadyExistsError
from app.application.users.dto import UserLoginData, UserRegisterData
from app.infra.database.mappings import metadata
from app.infra.database.unit_of_work import SqlAlchemyUnitOfWork
from types import SimpleNamespace
from app.application.auth.interactors import RegisterUser, LoginUser, RefreshTokens, Logout, VerifyAccessToken
from app.infra.gateways.user import SqlAlchemyUserGateway
from app.infra.gateways.refresh_token import SqlAlchemyRefreshTokenGateway
from app.infra.security.jwt_service import JWTService

pytestmark = pytest.mark.req("P.AUTH")


@pytest.fixture
async def session_factory():
    engine = create_async_engine("sqlite+aiosqlite:///:memory:")
    async with engine.begin() as conn:
        await conn.run_sync(metadata.create_all)
    factory = async_sessionmaker(bind=engine, expire_on_commit=False)
    yield factory
    await engine.dispose()


def _auth_interactors(session):
    dependencies = dict(
        uow=SqlAlchemyUnitOfWork(session),
        user_gateway=SqlAlchemyUserGateway(session),
        refresh_token_gateway=SqlAlchemyRefreshTokenGateway(session),
        jwt_service=JWTService(),
    )
    return SimpleNamespace(
        register=RegisterUser(**dependencies),
        login_user=LoginUser(**dependencies),
        refresh_tokens=RefreshTokens(**dependencies),
        logout=Logout(**dependencies),
        verify_access_token=VerifyAccessToken(**dependencies),
    )


async def test_register_creates_user_and_returns_token_pair(session_factory):
    async with session_factory() as session:
        interactors = _auth_interactors(session)
        body = UserRegisterData(login="new", password="password1", fullName="New User")
        response, refresh_token, max_age = await interactors.register(body)
        assert response.user.login == "new"
        assert response.user.role.value == "USER"
        assert response.user.createdBy == response.user.id
        assert response.accessToken
        assert refresh_token
        assert max_age > 0


async def test_register_rejects_duplicate_login(session_factory):
    async with session_factory() as session:
        interactors = _auth_interactors(session)
        await interactors.register(UserRegisterData(login="dup", password="password1", fullName="User One"))
    async with session_factory() as session:
        interactors = _auth_interactors(session)
        with pytest.raises(UserAlreadyExistsError):
            await interactors.register(UserRegisterData(login="dup", password="password2", fullName="User Two"))


async def test_login_with_correct_credentials_returns_token_pair(session_factory):
    async with session_factory() as session:
        interactors = _auth_interactors(session)
        await interactors.register(UserRegisterData(login="login", password="password1", fullName="Login User"))
    async with session_factory() as session:
        interactors = _auth_interactors(session)
        response, refresh_token, _ = await interactors.login_user(UserLoginData(login="login", password="password1"))
        assert response.user.login == "login"
        assert refresh_token


async def test_login_with_wrong_password_raises(session_factory):
    async with session_factory() as session:
        interactors = _auth_interactors(session)
        await interactors.register(UserRegisterData(login="wrongpw", password="password1", fullName="User"))
    async with session_factory() as session:
        interactors = _auth_interactors(session)
        with pytest.raises(InvalidCredentialsError):
            await interactors.login_user(UserLoginData(login="wrongpw", password="wrong-password"))


async def test_login_with_unknown_login_raises(session_factory):
    async with session_factory() as session:
        interactors = _auth_interactors(session)
        with pytest.raises(InvalidCredentialsError):
            await interactors.login_user(UserLoginData(login="ghost", password="password1"))


async def test_refresh_rotates_token_and_invalidates_old_one(session_factory):
    async with session_factory() as session:
        interactors = _auth_interactors(session)
        _, refresh_token, _ = await interactors.register(
            UserRegisterData(login="rotate", password="password1", fullName="User")
        )
    async with session_factory() as session:
        interactors = _auth_interactors(session)
        new_access, new_refresh, _ = await interactors.refresh_tokens(refresh_token)
        assert new_access.accessToken
        assert new_refresh != refresh_token
    async with session_factory() as session:
        interactors = _auth_interactors(session)
        with pytest.raises(InvalidCredentialsError):
            await interactors.refresh_tokens(refresh_token)


async def test_refresh_with_unknown_token_raises(session_factory):
    async with session_factory() as session:
        interactors = _auth_interactors(session)
        with pytest.raises(InvalidCredentialsError):
            await interactors.refresh_tokens("not-a-real-refresh-token")


async def test_logout_deletes_refresh_token_and_is_idempotent(session_factory):
    async with session_factory() as session:
        interactors = _auth_interactors(session)
        _, refresh_token, _ = await interactors.register(
            UserRegisterData(login="logout", password="password1", fullName="User")
        )
    async with session_factory() as session:
        interactors = _auth_interactors(session)
        await interactors.logout(refresh_token)
    async with session_factory() as session:
        interactors = _auth_interactors(session)
        with pytest.raises(InvalidCredentialsError):
            await interactors.refresh_tokens(refresh_token)
    async with session_factory() as session:
        interactors = _auth_interactors(session)
        await interactors.logout(refresh_token)


async def test_verify_access_token_returns_current_user_data(session_factory):
    async with session_factory() as session:
        interactors = _auth_interactors(session)
        response, _, _ = await interactors.register(
            UserRegisterData(login="verify", password="password1", fullName="User")
        )
        access_token = response.accessToken
    async with session_factory() as session:
        interactors = _auth_interactors(session)
        user_data = await interactors.verify_access_token(access_token)
        assert user_data.login == "verify"
