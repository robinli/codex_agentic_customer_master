from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.approvals.schemas import ApprovalRejectRequest, ApprovalSummary
from app.approvals.service import approve_request, get_approval, list_approvals, reject_request
from app.auth.dependencies import get_current_user
from app.auth.schemas import CurrentUser
from app.db import get_db

router = APIRouter(prefix="/approvals", tags=["approvals"])


@router.get("", response_model=list[ApprovalSummary])
def get_approvals(db: Session = Depends(get_db)) -> list[ApprovalSummary]:
    return list_approvals(db)


@router.get("/{approval_id}", response_model=ApprovalSummary)
def get_approval_detail(approval_id: str, db: Session = Depends(get_db)) -> ApprovalSummary:
    return get_approval(db, approval_id)


@router.post("/{approval_id}/approve", response_model=ApprovalSummary)
def approve(
    approval_id: str,
    db: Session = Depends(get_db),
    current_user: CurrentUser = Depends(get_current_user),
) -> ApprovalSummary:
    return approve_request(db, approval_id=approval_id, user=current_user)


@router.post("/{approval_id}/reject", response_model=ApprovalSummary)
def reject(
    approval_id: str,
    payload: ApprovalRejectRequest,
    db: Session = Depends(get_db),
    current_user: CurrentUser = Depends(get_current_user),
) -> ApprovalSummary:
    return reject_request(db, approval_id=approval_id, comment=payload.comment, user=current_user)
