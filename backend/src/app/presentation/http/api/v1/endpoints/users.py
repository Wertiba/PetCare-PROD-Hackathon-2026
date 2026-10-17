from dishka.integrations.fastapi import DishkaRoute, FromDishka
from fastapi import APIRouter, status

from app.application.users.dto import UserUpdateData
from app.application.users.interactors import GetMe, UpdateMe
from app.presentation.http.api.v1.dependencies import CurrentUserDep
from app.presentation.http.schemas.user import UserReadResponse, UserUpdateBody

router = APIRouter(prefix="/users", tags=["Users"], route_class=DishkaRoute)


@router.get("/me", response_model=UserReadResponse, status_code=status.HTTP_200_OK)
async def get_me(user: CurrentUserDep, interactor: FromDishka[GetMe]) -> UserReadResponse:
    return UserReadResponse.model_validate(await interactor(user.id), from_attributes=True)


@router.patch("/me", response_model=UserReadResponse, status_code=status.HTTP_200_OK)
async def update_me(user: CurrentUserDep, interactor: FromDishka[UpdateMe], body: UserUpdateBody) -> UserReadResponse:
    return UserReadResponse.model_validate(
        await interactor(user.id, UserUpdateData(changes=body.model_dump(exclude_unset=True))), from_attributes=True
    )
