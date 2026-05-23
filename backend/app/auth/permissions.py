from app.auth.schemas import CurrentUser
from app.common.errors import forbidden

ROLE_RANK = {
    "viewer": 1,
    "editor": 2,
    "approver": 3,
    "admin": 4,
}


def require_min_role(user: CurrentUser, minimum: str) -> None:
    actual = max((ROLE_RANK.get(role, 0) for role in user.roles), default=0)
    needed = ROLE_RANK[minimum]
    if actual < needed:
        raise forbidden(f"{minimum} role is required")


def require_any_role(user: CurrentUser, roles: set[str]) -> None:
    if not roles.intersection(set(user.roles)):
        raise forbidden("Insufficient role")

