import pytest
from fastapi import Response
from app.presentation.http.api.v1.utils.cookies import REFRESH_COOKIE_NAME, delete_refresh_cookie, set_refresh_cookie

pytestmark = pytest.mark.req("P.AUTH")


def test_set_refresh_cookie_sets_expected_attributes(http_config):
    response = Response()
    set_refresh_cookie(response, "raw-refresh-token", max_age_seconds=2592000, config=http_config)
    cookie_header = response.headers["set-cookie"]
    assert f"{REFRESH_COOKIE_NAME}=raw-refresh-token" in cookie_header
    assert "HttpOnly" in cookie_header
    assert "samesite=lax" in cookie_header.lower()
    assert "Path=/" in cookie_header
    assert "Max-Age=2592000" in cookie_header


def test_delete_refresh_cookie_expires_it(http_config):
    response = Response()
    delete_refresh_cookie(response, config=http_config)
    cookie_header = response.headers["set-cookie"]
    assert f"{REFRESH_COOKIE_NAME}=" in cookie_header
    assert "Max-Age=0" in cookie_header
