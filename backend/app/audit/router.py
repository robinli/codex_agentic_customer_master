from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.audit.schemas import AuditLogRead
from app.audit.service import list_audit_logs
from app.auth.dependencies import get_current_user
from app.auth.schemas import CurrentUser
from app.db import get_db

router = APIRouter(prefix="/audit-logs", tags=["audit"])


@router.get("", response_model=list[AuditLogRead])
def get_audit_logs(
    db: Session = Depends(get_db),
    current_user: CurrentUser = Depends(get_current_user),
) -> list[AuditLogRead]:
    return list_audit_logs(db, user=current_user)

