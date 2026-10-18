from typing import Annotated

from dishka.integrations.fastapi import FromDishka, inject
from fastapi import Depends, Request

from app.application.auth.interactors import VerifyAccessToken
from app.application.users.dto import UserData
from app.domain.users.errors import InvalidCredentialsError
from app.presentation.http.api.v1.utils.cookies import ACCESS_COOKIE_NAME


@inject
async def get_current_user(request: Request, verify: FromDishka[VerifyAccessToken]) -> UserData:
    auth_header = request.headers.get("Authorization")
    if auth_header is not None:
        if not auth_header.startswith("Bearer "):
            raise InvalidCredentialsError
        access_token = auth_header.split(" ", 1)[1]
    else:
        access_token = request.cookies.get(ACCESS_COOKIE_NAME)
    if not access_token:
        raise InvalidCredentialsError
    return await verify(access_token)


CurrentUserDep = Annotated[UserData, Depends(get_current_user)]
