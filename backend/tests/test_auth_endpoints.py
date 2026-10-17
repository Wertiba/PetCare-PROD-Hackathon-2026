import io
from pathlib import Path

import pytest
from alembic import command
from alembic.config import Config


def test_register_returns_201_and_sets_cookie(client):
    response = client.post(
        "/api/v1/auth/register", json={"login": "flow", "password": "password1", "fullName": "Flow User"}
    )
    assert response.status_code == 201
    body = response.json()
    assert body["user"]["login"] == "flow"
    assert "email" not in body["user"]
    assert body["user"]["role"] == "USER"
    assert "location" not in {k.lower() for k in response.headers}
    assert "refreshToken" in response.cookies


@pytest.mark.parametrize("login", ["", "x" * 256])
@pytest.mark.parametrize("endpoint", ["register", "login"])
def test_invalid_login_is_rejected(client, login, endpoint):
    response = client.post(
        f"/api/v1/auth/{endpoint}", json={"login": login, "password": "password1", "fullName": "Test User"}
    )
    assert response.status_code == 422
    assert any(error["field"] == "login" for error in response.json()["fieldErrors"])


@pytest.mark.parametrize("endpoint", ["register", "login"])
def test_email_does_not_replace_login(client, endpoint):
    response = client.post(
        f"/api/v1/auth/{endpoint}",
        json={"email": "old@example.com", "password": "password1", "fullName": "Test User"},
    )
    assert response.status_code == 422
    assert any(error["field"] == "login" for error in response.json()["fieldErrors"])


def test_login_migration_renames_identifier_and_unique_constraint():
    output = io.StringIO()
    config = Config(str(Path(__file__).parents[1] / "alembic.ini"), output_buffer=output)
    command.upgrade(config, "0004_epoch_timestamps:0005_user_login", sql=True)
    sql = output.getvalue()
    assert "RENAME email TO login" in sql
    assert "DROP CONSTRAINT uq_users_email" in sql
    assert "ADD CONSTRAINT uq_users_login UNIQUE (login)" in sql
    assert "DROP COLUMN" not in sql
    output = io.StringIO()
    config = Config(str(Path(__file__).parents[1] / "alembic.ini"), output_buffer=output)
    command.downgrade(config, "0005_user_login:0004_epoch_timestamps", sql=True)
    sql = output.getvalue()
    assert "RENAME login TO email" in sql
    assert "ADD CONSTRAINT uq_users_email UNIQUE (email)" in sql


def test_register_rejects_duplicate_login(client):
    payload = {"login": "dup", "password": "password1", "fullName": "User"}
    client.post("/api/v1/auth/register", json=payload)
    response = client.post("/api/v1/auth/register", json=payload)
    assert response.status_code == 409
    body = response.json()
    assert body["code"] == "LOGIN_ALREADY_EXISTS"
    assert body["details"] == {"field": "login", "value": "dup"}


def test_register_rejects_full_name_with_invalid_characters(client):
    response = client.post(
        "/api/v1/auth/register", json={"login": "badname", "password": "password1", "fullName": "User!!!"}
    )
    assert response.status_code == 422


def test_register_accepts_cyrillic_full_name(client):
    response = client.post(
        "/api/v1/auth/register",
        json={"login": "cyrillic", "password": "password1", "fullName": "Иван Иванов"},
    )
    assert response.status_code == 201


def test_validation_error_message_is_english(client):
    response = client.post("/api/v1/auth/register", json={"login": "not-an-login", "password": "x", "fullName": ""})
    assert response.status_code == 422
    assert response.json()["message"] == "Some fields are not correct."


def test_login_returns_200_and_sets_refresh_cookie(client):
    client.post(
        "/api/v1/auth/register", json={"login": "login", "password": "password1", "fullName": "Login User"}
    )
    response = client.post("/api/v1/auth/login", json={"login": "login", "password": "password1"})
    assert response.status_code == 200
    assert response.json()["user"]["login"] == "login"
    assert "refreshToken" in response.cookies


def test_login_with_wrong_password_returns_401(client):
    client.post(
        "/api/v1/auth/register", json={"login": "badpw", "password": "password1", "fullName": "User"}
    )
    for login, password in (("badpw", "wrong-password"), ("ghost", "password1")):
        response = client.post("/api/v1/auth/login", json={"login": login, "password": password})
        assert response.status_code == 401
        assert response.json()["code"] == "WRONG_LOGIN_OR_PASSWORD"
        assert response.json()["message"] == "Wrong login or password"
    bad_token = client.get("/api/v1/users/me", headers={"Authorization": "Bearer nonsense"})
    assert bad_token.status_code == 401
    assert bad_token.json()["code"] == "UNAUTHORIZED"


def test_refresh_rotates_cookie_and_invalidates_previous_refresh_token(client):
    register_response = client.post(
        "/api/v1/auth/register", json={"login": "rotate", "password": "password1", "fullName": "User"}
    )
    old_refresh_cookie = register_response.cookies["refreshToken"]
    refresh_response = client.post("/api/v1/auth/refresh")
    assert refresh_response.status_code == 200
    assert "accessToken" in refresh_response.json()
    new_refresh_cookie = refresh_response.cookies["refreshToken"]
    assert new_refresh_cookie != old_refresh_cookie
    client.cookies.set("refreshToken", old_refresh_cookie)
    reuse_response = client.post("/api/v1/auth/refresh")
    assert reuse_response.status_code == 401


def test_refresh_without_cookie_returns_401(client):
    response = client.post("/api/v1/auth/refresh")
    assert response.status_code == 401


def test_logout_clears_cookie_and_revokes_refresh_token(client):
    register_response = client.post(
        "/api/v1/auth/register", json={"login": "logout", "password": "password1", "fullName": "User"}
    )
    refresh_cookie = register_response.cookies["refreshToken"]
    logout_response = client.post("/api/v1/auth/logout")
    assert logout_response.status_code == 204
    client.cookies.set("refreshToken", refresh_cookie)
    reuse_response = client.post("/api/v1/auth/refresh")
    assert reuse_response.status_code == 401


def test_logout_without_cookie_returns_401(client):
    response = client.post("/api/v1/auth/logout")
    assert response.status_code == 401
