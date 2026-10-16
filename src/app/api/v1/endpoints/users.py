from fastapi import APIRouter, status

from app.api.v1.dependencies import CurrentUserDep, UserServiceDep
from app.core.schemas.user import UserReadResponse, UserUpdateBody

router = APIRouter(prefix="/users", tags=["Users"])


@router.get("/me", response_model=UserReadResponse, status_code=status.HTTP_200_OK)
async def get_me(user: CurrentUserDep, user_service: UserServiceDep) -> UserReadResponse:
    return await user_service.get_me(user.id)


@router.patch("/me", response_model=UserReadResponse, status_code=status.HTTP_200_OK)
async def update_me(user: CurrentUserDep, user_service: UserServiceDep, body: UserUpdateBody) -> UserReadResponse:
    return await user_service.update_me(user.id, body)
