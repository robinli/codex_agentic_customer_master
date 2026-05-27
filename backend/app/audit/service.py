import uuid

from fastapi.encoders import jsonable_encoder
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.audit.models import AuditLog
from app.auth.permissions import require_any_role
from app.auth.schemas import CurrentUser


def write_audit_log(
    db: Session,
    *,
    actor: CurrentUser | None,
    actor_type: str,
    action: str,
    target_type: str,
    target_id: str | None,
    before_data: dict | None = None,
    after_data: dict | None = None,
    metadata: dict | None = None,
) -> AuditLog:
    entry = AuditLog(
        actor_id=uuid.UUID(actor.id) if actor else None,
        actor_type=actor_type,
        action=action,
        target_type=target_type,
        target_id=uuid.UUID(target_id) if target_id else None,
        before_data=jsonable_encoder(before_data),
        after_data=jsonable_encoder(after_data),
        metadata_json=jsonable_encoder(metadata),
    )
    db.add(entry)
    return entry


def list_audit_logs(db: Session, *, user: CurrentUser) -> list[AuditLog]:
    require_any_role(user, {"admin"})
    stmt = select(AuditLog).order_by(AuditLog.created_at.desc()).limit(200)
    return list(db.scalars(stmt))
