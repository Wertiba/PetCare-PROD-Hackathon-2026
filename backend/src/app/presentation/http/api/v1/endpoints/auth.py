from dishka.integrations.fastapi import DishkaRoute, FromDishka
from fastapi import APIRouter, Request, Response, status

from app.application.auth.interactors import LoginUser, Logout, RefreshTokens, RegisterUser
from app.application.users.dto import UserLoginData, UserRegisterData
from app.domain.users.errors import InvalidCredentialsError, WrongLoginOrPasswordError
from app.infra.metrics import track
from app.presentation.http.api.v1.utils.cookies import REFRESH_COOKIE_NAME, delete_refresh_cookie, set_refresh_cookie
from app.presentation.http.schemas.responses import ErrorResponse
from app.presentation.http.schemas.token import AccessTokenResponse
from app.presentation.http.schemas.user import UserAndAccessTokenResponse, UserLoginBody, UserRegisterBody

router = APIRouter(prefix="/auth", tags=["Auth"], route_class=DishkaRoute)


@router.post("/register", response_model=UserAndAccessTokenResponse, status_code=status.HTTP_201_CREATED)
async def register(
    interactor: FromDishka[RegisterUser], user_data: UserRegisterBody, response: Response
) -> UserAndAccessTokenResponse:
    result, refresh_token, max_age = await interactor(UserRegisterData(**user_data.model_dump()))
    track("user", "registered")
    set_refresh_cookie(response, refresh_token, max_age_seconds=max_age)
    return UserAndAccessTokenResponse.model_validate(result, from_attributes=True)


@router.post(
    "/login",
    response_model=UserAndAccessTokenResponse,
    status_code=status.HTTP_200_OK,
    responses={
        status.HTTP_401_UNAUTHORIZED: {"model": ErrorResponse, "description": "WRONG_LOGIN_OR_PASSWORD"},
    },
)
async def login(
    interactor: FromDishka[LoginUser], user_data: UserLoginBody, response: Response
) -> UserAndAccessTokenResponse:
    try:
        result, refresh_token, max_age = await interactor(UserLoginData(**user_data.model_dump()))
    except WrongLoginOrPasswordError:
        track("user", "login_failed")
        raise
    track("user", "logged_in")
    set_refresh_cookie(response, refresh_token, max_age_seconds=max_age)
    return UserAndAccessTokenResponse.model_validate(result, from_attributes=True)


@router.post("/refresh", response_model=AccessTokenResponse, status_code=status.HTTP_200_OK)
async def refresh(interactor: FromDishka[RefreshTokens], request: Request, response: Response) -> AccessTokenResponse:
    raw_refresh_token = request.cookies.get(REFRESH_COOKIE_NAME)
    if not raw_refresh_token:
        raise InvalidCredentialsError
    result, new_refresh_token, max_age = await interactor(raw_refresh_token)
    set_refresh_cookie(response, new_refresh_token, max_age_seconds=max_age)
    return AccessTokenResponse.model_validate(result, from_attributes=True)


@router.post("/logout", status_code=status.HTTP_204_NO_CONTENT)
async def logout(interactor: FromDishka[Logout], request: Request, response: Response) -> None:
    raw_refresh_token = request.cookies.get(REFRESH_COOKIE_NAME)
    if not raw_refresh_token:
        raise InvalidCredentialsError
    await interactor(raw_refresh_token)
    delete_refresh_cookie(response)
