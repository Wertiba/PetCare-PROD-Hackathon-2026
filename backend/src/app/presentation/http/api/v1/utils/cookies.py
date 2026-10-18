from fastapi import Response

from app.infra.config import HttpConfig

ACCESS_COOKIE_NAME = "accessToken"
REFRESH_COOKIE_NAME = "refreshToken"


def set_cookie(response: Response, key: str, value: str, max_age_seconds: int, *, config: HttpConfig) -> None:
    response.set_cookie(
        key=key,
        value=value,
        max_age=max_age_seconds,
        httponly=True,
        secure=config.cookie_secure,
        samesite="lax",
        path="/",
    )


def set_access_cookie(response: Response, access_token: str, max_age_seconds: int, *, config: HttpConfig) -> None:
    set_cookie(response, ACCESS_COOKIE_NAME, access_token, max_age_seconds, config=config)


def set_refresh_cookie(response: Response, refresh_token: str, max_age_seconds: int, *, config: HttpConfig) -> None:
    set_cookie(response, REFRESH_COOKIE_NAME, refresh_token, max_age_seconds, config=config)


def delete_access_cookie(response: Response, *, config: HttpConfig) -> None:
    response.delete_cookie(
        key=ACCESS_COOKIE_NAME,
        path="/",
        httponly=True,
        secure=config.cookie_secure,
        samesite="lax",
    )


def delete_refresh_cookie(response: Response, *, config: HttpConfig) -> None:
    response.delete_cookie(
        key=REFRESH_COOKIE_NAME,
        path="/",
        httponly=True,
        secure=config.cookie_secure,
        samesite="lax",
    )
