from app.audit.service import write_audit_log
from app.auth.permissions import require_any_role
from app.auth.schemas import CurrentUser
from app.auth.user_store import create_user_record, get_user, get_user_by_email, list_users, update_user_record
from app.common.errors import bad_request, not_found
from app.users.schemas import UserCreate, UserUpdate
from sqlalchemy.orm import Session


def list_system_users(*, user: CurrentUser) -> list[dict]:
    require_any_role(user, {"admin"})
    return list_users()


def create_system_user(db: Session, *, payload: UserCreate, user: CurrentUser) -> dict:
    require_any_role(user, {"admin"})
    if get_user_by_email(payload.email):
        raise bad_request("email already exists")
    created = create_user_record(
        email=payload.email,
        name=payload.name,
        roles=payload.roles,
        password=payload.password,
        is_active=payload.is_active,
    )
    write_audit_log(
        db,
        actor=user,
        actor_type="user",
        action="user.create",
        target_type="user",
        target_id=created["id"],
        after_data={k: v for k, v in created.items() if k != "password"},
    )
    db.commit()
    return created


def update_system_user(db: Session, *, user_id: str, payload: UserUpdate, user: CurrentUser) -> dict:
    require_any_role(user, {"admin"})
    existing = get_user(user_id)
    if not existing:
        raise not_found("User not found")
    updates = payload.model_dump(exclude_unset=True)
    if not updates:
        raise bad_request("No fields to update")
    updated = update_user_record(user_id, updates)
    assert updated is not None
    write_audit_log(
        db,
        actor=user,
        actor_type="user",
        action="user.update",
        target_type="user",
        target_id=user_id,
        before_data={k: v for k, v in existing.items() if k != "password"},
        after_data={k: v for k, v in updated.items() if k != "password"},
    )
    db.commit()
    return updated
