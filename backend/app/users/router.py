from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.auth.dependencies import get_current_user
from app.auth.schemas import CurrentUser
from app.db import get_db
from app.users.schemas import UserCreate, UserRead, UserUpdate
from app.users.service import create_system_user, list_system_users, update_system_user

router = APIRouter(prefix="/settings/users", tags=["users"])


@router.get("", response_model=list[UserRead])
def get_users(current_user: CurrentUser = Depends(get_current_user)) -> list[UserRead]:
    return list_system_users(user=current_user)


@router.post("", response_model=UserRead)
def create_user(
    payload: UserCreate,
    db: Session = Depends(get_db),
    current_user: CurrentUser = Depends(get_current_user),
) -> UserRead:
    return create_system_user(db, payload=payload, user=current_user)


@router.patch("/{user_id}", response_model=UserRead)
def update_user(
    user_id: str,
    payload: UserUpdate,
    db: Session = Depends(get_db),
    current_user: CurrentUser = Depends(get_current_user),
) -> UserRead:
    return update_system_user(db, user_id=user_id, payload=payload, user=current_user)
