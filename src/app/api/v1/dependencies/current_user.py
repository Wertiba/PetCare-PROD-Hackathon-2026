from typing import Annotated

from fastapi import Depends, Request

from app.api.v1.dependencies.services.auth_service import AuthServiceDep
from app.core.exceptions.user_exs import InvalidCredentialsError
from app.core.schemas.user import UserData


async def get_current_user(request: Request, auth_service: AuthServiceDep) -> UserData:
    auth_header = request.headers.get("Authorization", "")
    if not auth_header.startswith("Bearer "):
        raise InvalidCredentialsError
    token = auth_header.split(" ", 1)[1]
    return await auth_service.verify_access_token(token)


CurrentUserDep = Annotated[UserData, Depends(get_current_user)]
