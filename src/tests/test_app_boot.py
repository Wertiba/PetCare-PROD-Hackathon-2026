# src/tests/test_app_boot.py
from fastapi.testclient import TestClient

from app.main import app


def test_app_imports_and_liveness_responds():
    client = TestClient(app)
    response = client.get("/health/liveness")
    assert response.status_code == 200
    assert response.json()["status"] == "ok"


def test_user_role_has_no_typo():
    from app.core.schemas.user import UserRole

    assert UserRole.ADMIN.value == "ADMIN"
    assert not hasattr(UserRole, "ADMN")
