def test_register_returns_201_and_sets_cookie(client):
    response = client.post(
        "/api/v1/auth/register",
        json={"email": "flow@petcare.dev", "password": "password1", "fullName": "Flow User"},
    )

    assert response.status_code == 201
    body = response.json()
    assert body["user"]["email"] == "flow@petcare.dev"
    assert body["user"]["role"] == "USER"
    assert "location" not in {k.lower() for k in response.headers}
    assert "refreshToken" in response.cookies


def test_register_rejects_duplicate_email(client):
    payload = {"email": "dup@petcare.dev", "password": "password1", "fullName": "User"}
    client.post("/api/v1/auth/register", json=payload)
    response = client.post("/api/v1/auth/register", json=payload)

    assert response.status_code == 409
    body = response.json()
    assert body["code"] == "EMAIL_ALREADY_EXISTS"
    assert body["details"] == {"field": "email", "value": "dup@petcare.dev"}


def test_register_rejects_full_name_with_invalid_characters(client):
    response = client.post(
        "/api/v1/auth/register",
        json={"email": "badname@petcare.dev", "password": "password1", "fullName": "User!!!"},
    )
    assert response.status_code == 422


def test_register_accepts_cyrillic_full_name(client):
    response = client.post(
        "/api/v1/auth/register",
        json={"email": "cyrillic@petcare.dev", "password": "password1", "fullName": "Иван Иванов"},
    )
    assert response.status_code == 201


def test_validation_error_message_is_english(client):
    response = client.post("/api/v1/auth/register", json={"email": "not-an-email", "password": "x", "fullName": ""})
    assert response.status_code == 422
    assert response.json()["message"] == "Some fields are not correct."


def test_login_returns_200_and_sets_refresh_cookie(client):
    client.post(
        "/api/v1/auth/register",
        json={"email": "login@petcare.dev", "password": "password1", "fullName": "Login User"},
    )

    response = client.post("/api/v1/auth/login", json={"email": "login@petcare.dev", "password": "password1"})

    assert response.status_code == 200
    assert response.json()["user"]["email"] == "login@petcare.dev"
    assert "refreshToken" in response.cookies


def test_login_with_wrong_password_returns_401(client):
    client.post(
        "/api/v1/auth/register",
        json={"email": "badpw@petcare.dev", "password": "password1", "fullName": "User"},
    )

    response = client.post("/api/v1/auth/login", json={"email": "badpw@petcare.dev", "password": "wrong-password"})
    assert response.status_code == 401


def test_refresh_rotates_cookie_and_invalidates_previous_refresh_token(client):
    register_response = client.post(
        "/api/v1/auth/register",
        json={"email": "rotate@petcare.dev", "password": "password1", "fullName": "User"},
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
        "/api/v1/auth/register",
        json={"email": "logout@petcare.dev", "password": "password1", "fullName": "User"},
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
