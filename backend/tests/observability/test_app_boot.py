from types import SimpleNamespace
from unittest.mock import AsyncMock, Mock

import jwt
from dishka import Provider, Scope, provide

import pytest
from fastapi.testclient import TestClient

from app.application.ports.tokens import TokenService
from app.application.ports.avatar_generator import AvatarGenerator
from app.bootstrap import build_container
from app.infra.config import AppConfig, AvatarConfig, DatabaseConfig, HttpConfig, SecurityConfig
from app.infra.database.db_helper import DatabaseHelper
from app.main import app, create_app

pytestmark = pytest.mark.req("P.OBS")


def test_app_imports_and_liveness_responds():
    client = TestClient(app)
    response = client.get("/health/liveness")
    assert response.status_code == 200
    assert response.json()["status"] == "ok"


def test_user_role_has_no_typo():
    from app.presentation.http.schemas.user import UserRole

    assert UserRole.ADMIN.value == "ADMIN"
    assert not hasattr(UserRole, "ADMN")


async def test_app_uses_injected_configs_for_title_cors_cookies_and_jwt(db_session_factory, monkeypatch):
    monkeypatch.setenv("APP_NAME", "Environment app")
    monkeypatch.setenv("APP_COOKIE_SECURE", "true")
    http_config = HttpConfig(APP_COOKIE_SECURE=False, APP_CORS_ALLOWED_ORIGINS="https://frontend.example")
    security_config = SecurityConfig(APP_SECURITY_JWT_SECRET="injected-jwt-secret-for-tests-0123456789")

    class Overrides(Provider):
        scope = Scope.APP

        @provide(override=True)
        def app_config(self) -> AppConfig:
            return AppConfig(APP_NAME="Injected app")

        @provide(override=True)
        def http(self) -> HttpConfig:
            return http_config

        @provide(override=True)
        def security(self) -> SecurityConfig:
            return security_config

        @provide(override=True)
        def database(self) -> DatabaseHelper:
            return SimpleNamespace(session_factory=db_session_factory)

    container = build_container(Overrides())
    application = create_app(container)
    assert application.title == "Injected app"
    assert container.get_sync(HttpConfig) is http_config
    assert container.get_sync(TokenService).secret_key == security_config.jwt_secret
    with TestClient(application, base_url="https://testserver") as client:
        response = client.post(
            "/api/v1/auth/register",
            headers={"Origin": "https://frontend.example"},
            json={"login": "injected", "password": "password1", "fullName": "Injected user"},
        )
        assert response.status_code == 201, response.text
        assert response.headers["access-control-allow-origin"] == "https://frontend.example"
        assert "Secure" not in response.headers["set-cookie"]
        token = response.json()["accessToken"]
        assert jwt.decode(token, security_config.jwt_secret, algorithms=[security_config.algorithm])["type"] == "access"


async def test_database_is_lazy_uses_injected_config_and_closes_with_container(monkeypatch):
    config = DatabaseConfig(
        DB_HOST="injected-host",
        DB_NAME="injected-db",
        DB_USER="injected-user",
        DB_PASSWORD="injected-password",
        DB_PORT=5433,
    )
    database = SimpleNamespace(dispose=AsyncMock())
    factory = Mock(return_value=database)
    monkeypatch.setattr("app.infra.database.di.DatabaseHelper", factory)

    class Overrides(Provider):
        @provide(scope=Scope.APP, override=True)
        def database_config(self) -> DatabaseConfig:
            return config

    container = build_container(Overrides())
    factory.assert_not_called()
    try:
        assert await container.get(DatabaseHelper) is database
        assert await container.get(DatabaseHelper) is database
        assert factory.call_count == 1
        url = factory.call_args.kwargs["url"]
        assert (url.host, url.port, url.database) == ("injected-host", 5433, "injected-db")
    finally:
        await container.close()
    database.dispose.assert_awaited_once()


async def test_avatar_provider_uses_injected_config(monkeypatch):
    monkeypatch.setenv("LLM_PROXY_API_KEY", "environment-key")
    config = AvatarConfig(
        LLM_PROXY_URL="https://injected.example",
        LLM_PROXY_API_KEY="injected-key",
        LLM_AVATAR_MODEL="injected-model",
        LLM_IMAGE_TOOL_MODEL="injected-tool",
        LLM_AVATAR_TIMEOUT=42,
    )

    class Overrides(Provider):
        @provide(scope=Scope.APP, override=True)
        def avatar_config(self) -> AvatarConfig:
            return config

    container = build_container(Overrides())
    try:
        generator = await container.get(AvatarGenerator)
        assert generator.base_url == config.base_url
        assert generator.api_key == config.api_key
        assert generator.model == config.model
        assert generator.tool_model == config.tool_model
        assert generator.timeout == config.timeout
    finally:
        await container.close()
