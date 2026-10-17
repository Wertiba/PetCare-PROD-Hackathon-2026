from typing import Annotated

from dishka.integrations.fastapi import FromDishka, inject
from fastapi import Depends, Request

from app.application.auth.interactors import VerifyAccessToken
from app.application.users.dto import UserData
from app.domain.users.errors import InvalidCredentialsError


@inject
async def get_current_user(request: Request, verify: FromDishka[VerifyAccessToken]) -> UserData:
    auth_header = request.headers.get("Authorization", "")
    if not auth_header.startswith("Bearer "):
        raise InvalidCredentialsError
    return await verify(auth_header.split(" ", 1)[1])


CurrentUserDep = Annotated[UserData, Depends(get_current_user)]
