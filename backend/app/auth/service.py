from datetime import datetime, timedelta, timezone

import jwt

from app.auth.schemas import CurrentUser
from app.auth.user_store import get_user_by_email, list_users
from app.common.errors import forbidden
from app.config import get_settings


def authenticate_user(email: str, password: str) -> CurrentUser | None:
    for user in list_users():
        if user["email"].lower() == email.lower() and user["password"] == password and user.get("is_active", True):
            return CurrentUser(
                id=user["id"],
                email=user["email"],
                name=user["name"],
                roles=user["roles"],
            )
    return None


def create_access_token(user: CurrentUser) -> str:
    settings = get_settings()
    now = datetime.now(timezone.utc)
    payload = {
        "sub": user.id,
        "email": user.email,
        "name": user.name,
        "roles": user.roles,
        "iat": int(now.timestamp()),
        "exp": int((now + timedelta(minutes=settings.jwt_expire_minutes)).timestamp()),
    }
    return jwt.encode(payload, settings.jwt_secret, algorithm=settings.jwt_algorithm)


def decode_access_token(token: str) -> CurrentUser:
    settings = get_settings()
    try:
        payload = jwt.decode(token, settings.jwt_secret, algorithms=[settings.jwt_algorithm])
        return CurrentUser(
            id=payload["sub"],
            email=payload["email"],
            name=payload["name"],
            roles=payload["roles"],
        )
    except Exception as exc:
        raise forbidden("Invalid or expired token") from exc


def build_current_user_from_record(user: dict) -> CurrentUser:
    return CurrentUser(
        id=user["id"],
        email=user["email"],
        name=user["name"],
        roles=user["roles"],
    )


def get_current_user_record(email: str) -> dict | None:
    return get_user_by_email(email)
