from dishka.integrations.fastapi import DishkaRoute, FromDishka
from fastapi import APIRouter, Response, status

from app.application.ports.database_health import DatabaseHealth
from app.presentation.http.schemas.responses import PingResponse

router = APIRouter(route_class=DishkaRoute, prefix="/health", tags=["Health"])


@router.get("/liveness", response_model=PingResponse, status_code=status.HTTP_200_OK)
async def liveness() -> PingResponse:
    return PingResponse(status="ok")


@router.get("/readiness", status_code=status.HTTP_200_OK)
async def readiness(response: Response, health: FromDishka[DatabaseHealth]) -> dict:
    checks = {}
    try:
        await health.check()
        checks["database"] = "ready"
    except Exception as e:
        checks["database"] = f"not ready: {e}"
        response.status_code = status.HTTP_503_SERVICE_UNAVAILABLE
        return {"status": "not ready", "checks": checks}

    return {"status": "ready", "checks": checks}
