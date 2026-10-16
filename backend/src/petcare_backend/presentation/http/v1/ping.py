from fastapi import APIRouter, Response, status

router = APIRouter()


@router.get("/ping", status_code=status.HTTP_200_OK)
def ping() -> Response:
    return Response(status_code=status.HTTP_200_OK)
