from typing import Annotated

from fastapi import Depends, Header
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer

from app.auth.schemas import CurrentUser
from app.auth.service import decode_access_token

bearer_scheme = HTTPBearer(auto_error=False)


def get_current_user(
    authorization: Annotated[HTTPAuthorizationCredentials | None, Depends(bearer_scheme)],
    x_user_id: str = Header(default="00000000-0000-0000-0000-000000000001"),
    x_user_email: str = Header(default="editor@example.com"),
    x_user_name: str = Header(default="Editor User"),
    x_user_roles: str = Header(default="editor"),
) -> CurrentUser:
    if authorization and authorization.scheme.lower() == "bearer":
        return decode_access_token(authorization.credentials)
    return CurrentUser(
        id=x_user_id,
        email=x_user_email,
        name=x_user_name,
        roles=[role.strip() for role in x_user_roles.split(",") if role.strip()],
    )
