import uuid
from datetime import datetime, timezone

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.approvals.models import ApprovalRequest
from app.audit.service import write_audit_log
from app.auth.permissions import require_any_role
from app.auth.schemas import CurrentUser
from app.common.errors import bad_request, forbidden, not_found
from app.customers.models import Customer


def list_approvals(db: Session) -> list[ApprovalRequest]:
    return list(db.scalars(select(ApprovalRequest).order_by(ApprovalRequest.created_at.desc())))


def get_approval(db: Session, approval_id: str) -> ApprovalRequest:
    approval = db.get(ApprovalRequest, uuid.UUID(approval_id))
    if not approval:
        raise not_found("Approval request not found")
    return approval


def create_approval_request(
    db: Session,
    *,
    target_type: str,
    target_id: str,
    action: str,
    risk_level: str,
    before_data: dict | None,
    after_data: dict | None,
    reason: str,
    requested_by: str,
) -> ApprovalRequest:
    approval = ApprovalRequest(
        target_type=target_type,
        target_id=uuid.UUID(target_id),
        action=action,
        risk_level=risk_level,
        before_data=before_data,
        after_data=after_data,
        reason=reason,
        requested_by=uuid.UUID(requested_by),
    )
    db.add(approval)
    db.flush()
    return approval


def approve_request(db: Session, *, approval_id: str, user: CurrentUser) -> ApprovalRequest:
    require_any_role(user, {"approver", "admin"})
    approval = db.get(ApprovalRequest, uuid.UUID(approval_id))
    if not approval:
        raise not_found("Approval request not found")
    if approval.requested_by == uuid.UUID(user.id):
        raise forbidden("Approver cannot approve own request")
    if approval.status != "pending":
        raise bad_request("Only pending requests can be approved")

    if approval.target_type == "customer":
        customer = db.get(Customer, approval.target_id)
        if not customer:
            raise not_found("Target customer not found")
        before_data = {
            "status": customer.status,
            "tax_id": customer.tax_id,
            "payment_terms": customer.payment_terms,
            "credit_limit": float(customer.credit_limit) if customer.credit_limit is not None else None,
        }
        if approval.action == "disable":
            customer.status = "inactive"
        elif approval.after_data:
            for field, value in approval.after_data.items():
                setattr(customer, field, value)
        customer.updated_by = uuid.UUID(user.id)
        write_audit_log(
            db,
            actor=user,
            actor_type="user",
            action="approval.approve",
            target_type="approval",
            target_id=str(approval.id),
            before_data={"approval_status": "pending", "customer": before_data},
            after_data={"approval_status": "approved", "customer": approval.after_data},
        )

    approval.status = "approved"
    approval.reviewed_by = uuid.UUID(user.id)
    approval.reviewed_at = datetime.now(timezone.utc)
    db.commit()
    db.refresh(approval)
    return approval


def reject_request(db: Session, *, approval_id: str, comment: str, user: CurrentUser) -> ApprovalRequest:
    require_any_role(user, {"approver", "admin"})
    approval = db.get(ApprovalRequest, uuid.UUID(approval_id))
    if not approval:
        raise not_found("Approval request not found")
    if approval.requested_by == uuid.UUID(user.id):
        raise forbidden("Approver cannot reject own request")
    if approval.status != "pending":
        raise bad_request("Only pending requests can be rejected")
    approval.status = "rejected"
    approval.reviewed_by = uuid.UUID(user.id)
    approval.reviewed_at = datetime.now(timezone.utc)
    write_audit_log(
        db,
        actor=user,
        actor_type="user",
        action="approval.reject",
        target_type="approval",
        target_id=str(approval.id),
        before_data={"approval_status": "pending"},
        after_data={"approval_status": "rejected", "comment": comment},
    )
    db.commit()
    db.refresh(approval)
    return approval
