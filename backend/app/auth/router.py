from fastapi import APIRouter, Depends

from app.auth.dependencies import get_current_user
from app.auth.schemas import CurrentUser, LoginRequest, TokenResponse
from app.auth.service import authenticate_user, create_access_token
from app.common.errors import forbidden

router = APIRouter(tags=["auth"])


@router.post("/auth/login", response_model=TokenResponse)
def login(payload: LoginRequest) -> TokenResponse:
    user = authenticate_user(payload.email, payload.password)
    if not user:
        raise forbidden("Invalid email or password")
    token = create_access_token(user)
    return TokenResponse(access_token=token, user=user)


@router.get("/me", response_model=CurrentUser)
def get_me(current_user: CurrentUser = Depends(get_current_user)) -> CurrentUser:
    return current_user
