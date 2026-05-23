import json
from pathlib import Path
from typing import Any
import uuid

from app.config import get_settings


USER_STORE_PATH = Path(__file__).resolve().parents[2] / "data" / "users.json"


def _default_users() -> list[dict[str, Any]]:
    settings = get_settings()
    return json.loads(settings.demo_users_json)


def ensure_user_store() -> None:
    USER_STORE_PATH.parent.mkdir(parents=True, exist_ok=True)
    if not USER_STORE_PATH.exists():
        USER_STORE_PATH.write_text(json.dumps(_default_users(), indent=2, ensure_ascii=False), encoding="utf-8")


def load_users() -> list[dict[str, Any]]:
    ensure_user_store()
    return json.loads(USER_STORE_PATH.read_text(encoding="utf-8"))


def save_users(users: list[dict[str, Any]]) -> None:
    ensure_user_store()
    USER_STORE_PATH.write_text(json.dumps(users, indent=2, ensure_ascii=False), encoding="utf-8")


def list_users() -> list[dict[str, Any]]:
    return load_users()


def get_user(user_id: str) -> dict[str, Any] | None:
    return next((user for user in load_users() if user["id"] == user_id), None)


def get_user_by_email(email: str) -> dict[str, Any] | None:
    return next((user for user in load_users() if user["email"].lower() == email.lower()), None)


def create_user_record(*, email: str, name: str, roles: list[str], password: str, is_active: bool = True) -> dict[str, Any]:
    users = load_users()
    user = {
        "id": str(uuid.uuid4()),
        "email": email,
        "name": name,
        "roles": roles,
        "password": password,
        "is_active": is_active,
    }
    users.append(user)
    save_users(users)
    return user


def update_user_record(user_id: str, updates: dict[str, Any]) -> dict[str, Any] | None:
    users = load_users()
    for index, user in enumerate(users):
        if user["id"] == user_id:
            users[index] = {**user, **updates}
            save_users(users)
            return users[index]
    return None
