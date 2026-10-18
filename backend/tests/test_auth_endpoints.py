import io
from pathlib import Path

import pytest
from alembic import command
from alembic.config import Config

pytestmark = pytest.mark.req("P.AUTH")


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
    assert response.cookies["accessToken"] == body["accessToken"]
    access_cookie = next(
        header for header in response.headers.get_list("set-cookie") if header.startswith("accessToken=")
    )
    assert f"Max-Age={body['expiresIn']}" in access_cookie


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


@pytest.mark.req("7.1")
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


def test_register_accepts_full_name_with_yo(client):
    response = client.post(
        "/api/v1/auth/register",
        json={"login": "yo", "password": "password1", "fullName": "Пётр Семёнов"},
    )
    assert response.status_code == 201


@pytest.mark.req("7.1")
def test_validation_error_message_is_english(client):
    response = client.post("/api/v1/auth/register", json={"login": "not-an-login", "password": "x", "fullName": ""})
    assert response.status_code == 422
    assert response.json()["message"] == "Some fields are not correct."


def test_login_returns_200_and_sets_both_cookies(client):
    client.post("/api/v1/auth/register", json={"login": "login", "password": "password1", "fullName": "Login User"})
    response = client.post("/api/v1/auth/login", json={"login": "login", "password": "password1"})
    assert response.status_code == 200
    assert response.json()["user"]["login"] == "login"
    assert "refreshToken" in response.cookies
    assert response.cookies["accessToken"] == response.json()["accessToken"]


def test_login_with_wrong_password_returns_401(client):
    client.post("/api/v1/auth/register", json={"login": "badpw", "password": "password1", "fullName": "User"})
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
    assert refresh_response.cookies["accessToken"] == refresh_response.json()["accessToken"]
    access_cookie = next(
        header for header in refresh_response.headers.get_list("set-cookie") if header.startswith("accessToken=")
    )
    assert f"Max-Age={refresh_response.json()['expiresIn']}" in access_cookie
    new_refresh_cookie = refresh_response.cookies["refreshToken"]
    assert new_refresh_cookie != old_refresh_cookie
    client.cookies.set("refreshToken", old_refresh_cookie)
    reuse_response = client.post("/api/v1/auth/refresh")
    assert reuse_response.status_code == 401


def test_refresh_without_cookie_returns_401(client):
    response = client.post("/api/v1/auth/refresh")
    assert response.status_code == 401


def test_logout_clears_both_cookies_and_revokes_refresh_token(client):
    register_response = client.post(
        "/api/v1/auth/register", json={"login": "logout", "password": "password1", "fullName": "User"}
    )
    refresh_cookie = register_response.cookies["refreshToken"]
    logout_response = client.post("/api/v1/auth/logout")
    assert logout_response.status_code == 204
    assert "accessToken" not in client.cookies
    assert "refreshToken" not in client.cookies
    assert client.get("/api/v1/users/me").status_code == 401
    client.cookies.set("refreshToken", refresh_cookie)
    reuse_response = client.post("/api/v1/auth/refresh")
    assert reuse_response.status_code == 401


def test_logout_without_cookie_returns_401(client):
    response = client.post("/api/v1/auth/logout")
    assert response.status_code == 401


@pytest.mark.parametrize("endpoint", ["register", "login", "refresh"])
def test_access_cookie_authenticates_without_authorization_header(client, endpoint):
    response = client.post(
        "/api/v1/auth/register", json={"login": "cookie", "password": "password1", "fullName": "Cookie User"}
    )
    if endpoint == "login":
        client.cookies.clear()
        response = client.post("/api/v1/auth/login", json={"login": "cookie", "password": "password1"})
    elif endpoint == "refresh":
        client.cookies.delete("accessToken")
        response = client.post("/api/v1/auth/refresh")
    assert response.status_code in (200, 201)
    me = client.get("/api/v1/users/me")
    assert me.status_code == 200
    assert me.json()["login"] == "cookie"


def test_bearer_authentication_still_works_without_cookies(client):
    response = client.post(
        "/api/v1/auth/register", json={"login": "bearer", "password": "password1", "fullName": "Bearer User"}
    )
    token = response.json()["accessToken"]
    client.cookies.clear()
    me = client.get("/api/v1/users/me", headers={"Authorization": f"Bearer {token}"})
    assert me.status_code == 200
    assert me.json()["login"] == "bearer"


def test_bearer_header_takes_precedence_over_access_cookie(client):
    first = client.post(
        "/api/v1/auth/register", json={"login": "first", "password": "password1", "fullName": "First User"}
    )
    token = first.json()["accessToken"]
    client.post("/api/v1/auth/register", json={"login": "second", "password": "password1", "fullName": "Second User"})
    me = client.get("/api/v1/users/me", headers={"Authorization": f"Bearer {token}"})
    assert me.status_code == 200
    assert me.json()["login"] == "first"


@pytest.mark.parametrize("authorization", ["Bearer invalid", "Bearer ", "Basic invalid", ""])
def test_invalid_authorization_header_does_not_fall_back_to_cookie(client, authorization):
    client.post("/api/v1/auth/register", json={"login": "cookie", "password": "password1", "fullName": "Cookie User"})
    response = client.get("/api/v1/users/me", headers={"Authorization": authorization})
    assert response.status_code == 401


def test_invalid_access_cookie_is_rejected(client):
    client.cookies.set("accessToken", "invalid")
    assert client.get("/api/v1/users/me").status_code == 401


@pytest.mark.parametrize("schema_name", ["AccessTokenResponse", "UserAndAccessTokenResponse"])
def test_access_token_body_field_is_deprecated_but_still_required(client, schema_name):
    schema = client.get("/openapi.json").json()["components"]["schemas"][schema_name]
    assert schema["properties"]["accessToken"]["deprecated"] is True
    assert "HttpOnly accessToken cookie" in schema["properties"]["accessToken"]["description"]
    assert "accessToken" in schema["required"]
