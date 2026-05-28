import uuid
from decimal import Decimal

from sqlalchemy.orm import Session

from app.approvals.service import create_approval_request
from app.audit.service import write_audit_log
from app.auth.permissions import require_min_role
from app.auth.schemas import CurrentUser
from app.common.errors import bad_request, not_found
from app.common.pagination import Page, build_page
from app.customers.models import Customer, CustomerAddress, CustomerContact
from app.customers.repository import (
    find_customer_by_code,
    find_customer_by_tax_id,
    get_customer,
    search_customers,
)
from app.customers.schemas import (
    CustomerAddressCreate,
    CustomerAddressUpdate,
    CustomerContactCreate,
    CustomerContactUpdate,
    CustomerCreate,
    CustomerListItem,
    CustomerUpdate,
    MutationResult,
)

SENSITIVE_FIELDS = {"tax_id", "payment_terms", "credit_limit", "status"}


def list_customers(
    db: Session,
    *,
    q: str | None,
    status: str | None,
    customer_type: str | None,
    page: int,
    page_size: int,
) -> Page[CustomerListItem]:
    items, total = search_customers(
        db,
        q=q,
        status=status,
        customer_type=customer_type,
        page=page,
        page_size=page_size,
    )
    return build_page(items=items, page=page, page_size=page_size, total=total)


def create_customer(db: Session, *, payload: CustomerCreate, user: CurrentUser) -> Customer:
    require_min_role(user, "editor")
    if find_customer_by_code(db, payload.customer_code):
        raise bad_request("customer_code already exists")
    if payload.tax_id and find_customer_by_tax_id(db, payload.tax_id):
        raise bad_request("tax_id already exists")

    customer = Customer(
        customer_code=payload.customer_code,
        customer_name=payload.customer_name,
        tax_id=payload.tax_id,
        customer_type=payload.customer_type,
        status=payload.status,
        industry=payload.industry,
        phone=payload.phone,
        email=payload.email,
        website=payload.website,
        payment_terms=payload.payment_terms,
        credit_limit=payload.credit_limit,
        sales_owner_id=uuid.UUID(payload.sales_owner_id) if payload.sales_owner_id else None,
        note=payload.note,
        created_by=uuid.UUID(user.id),
        updated_by=uuid.UUID(user.id),
    )
    customer.contacts = [CustomerContact(**contact.model_dump()) for contact in payload.contacts]
    customer.addresses = [CustomerAddress(**address.model_dump()) for address in payload.addresses]
    db.add(customer)
    db.flush()
    write_audit_log(
        db,
        actor=user,
        actor_type="user",
        action="customer.create",
        target_type="customer",
        target_id=str(customer.id),
        after_data=payload.model_dump(mode="json"),
    )
    db.commit()
    db.refresh(customer)
    return customer


def get_customer_or_404(db: Session, customer_id: str) -> Customer:
    customer = get_customer(db, customer_id)
    if not customer:
        raise not_found("Customer not found")
    return customer


def update_customer(
    db: Session,
    *,
    customer_id: str,
    payload: CustomerUpdate,
    user: CurrentUser,
    reason: str | None = None,
) -> MutationResult:
    require_min_role(user, "editor")
    customer = get_customer_or_404(db, customer_id)
    updates = payload.model_dump(exclude_unset=True)
    if not updates:
        raise bad_request("No fields to update")

    if "tax_id" in updates and updates["tax_id"] != customer.tax_id and updates["tax_id"]:
        existing = find_customer_by_tax_id(db, updates["tax_id"])
        if existing and str(existing.id) != customer_id:
            raise bad_request("tax_id already exists")

    sensitive = {field: value for field, value in updates.items() if field in SENSITIVE_FIELDS}
    if sensitive:
        approval = create_approval_request(
            db,
            target_type="customer",
            target_id=customer_id,
            action="update",
            risk_level="high",
            before_data={field: getattr(customer, field) for field in sensitive},
            after_data=sensitive,
            reason=reason or "Sensitive field change requested",
            requested_by=user.id,
        )
        write_audit_log(
            db,
            actor=user,
            actor_type="user",
            action="customer.update.approval_requested",
            target_type="approval",
            target_id=str(approval.id),
            before_data={field: getattr(customer, field) for field in sensitive},
            after_data=sensitive,
        )
        db.commit()
        db.refresh(approval)
        return MutationResult(
            status="approval_required",
            message="Sensitive field change submitted for approval",
            approval_request_id=str(approval.id),
        )

    before = {field: getattr(customer, field) for field in updates}
    for field, value in updates.items():
        setattr(customer, field, value)
    customer.updated_by = uuid.UUID(user.id)
    write_audit_log(
        db,
        actor=user,
        actor_type="user",
        action="customer.update",
        target_type="customer",
        target_id=customer_id,
        before_data=before,
        after_data=updates,
    )
    db.commit()
    db.refresh(customer)
    return MutationResult(
        status="updated",
        message="Customer updated",
        data={"id": str(customer.id)},
    )


def disable_customer_request(db: Session, *, customer_id: str, reason: str, user: CurrentUser) -> MutationResult:
    require_min_role(user, "editor")
    customer = get_customer_or_404(db, customer_id)
    approval = create_approval_request(
        db,
        target_type="customer",
        target_id=customer_id,
        action="disable",
        risk_level="high",
        before_data={"status": customer.status},
        after_data={"status": "inactive"},
        reason=reason,
        requested_by=user.id,
    )
    write_audit_log(
        db,
        actor=user,
        actor_type="user",
        action="customer.disable_request",
        target_type="approval",
        target_id=str(approval.id),
        before_data={"status": customer.status},
        after_data={"status": "inactive", "reason": reason},
    )
    db.commit()
    db.refresh(approval)
    return MutationResult(
        status="approval_required",
        message="Disable request submitted",
        approval_request_id=str(approval.id),
    )


def add_contact(db: Session, *, customer_id: str, payload: CustomerContactCreate, user: CurrentUser) -> CustomerContact:
    require_min_role(user, "editor")
    customer = get_customer_or_404(db, customer_id)
    contact = CustomerContact(customer_id=customer.id, **payload.model_dump())
    db.add(contact)
    db.flush()
    write_audit_log(
        db,
        actor=user,
        actor_type="user",
        action="customer.contact.create",
        target_type="customer",
        target_id=customer_id,
        after_data=payload.model_dump(mode="json"),
    )
    db.commit()
    db.refresh(contact)
    return contact


def update_contact(
    db: Session,
    *,
    customer_id: str,
    contact_id: str,
    payload: CustomerContactUpdate,
    user: CurrentUser,
) -> CustomerContact:
    require_min_role(user, "editor")
    customer = get_customer_or_404(db, customer_id)
    contact = next((item for item in customer.contacts if str(item.id) == contact_id), None)
    if not contact:
        raise not_found("Contact not found")
    updates = payload.model_dump(exclude_unset=True)
    if not updates:
        raise bad_request("No fields to update")
    before = {field: getattr(contact, field) for field in updates}
    for field, value in updates.items():
        setattr(contact, field, value)
    write_audit_log(
        db,
        actor=user,
        actor_type="user",
        action="customer.contact.update",
        target_type="customer",
        target_id=customer_id,
        before_data=before,
        after_data=updates,
    )
    db.commit()
    db.refresh(contact)
    return contact


def delete_contact(db: Session, *, customer_id: str, contact_id: str, user: CurrentUser) -> MutationResult:
    require_min_role(user, "editor")
    customer = get_customer_or_404(db, customer_id)
    contact = next((item for item in customer.contacts if str(item.id) == contact_id), None)
    if not contact:
        raise not_found("Contact not found")
    before = {"id": str(contact.id), "name": contact.name, "email": contact.email}
    db.delete(contact)
    write_audit_log(
        db,
        actor=user,
        actor_type="user",
        action="customer.contact.delete",
        target_type="customer",
        target_id=customer_id,
        before_data=before,
    )
    db.commit()
    return MutationResult(status="deleted", message="Contact deleted")


def add_address(db: Session, *, customer_id: str, payload: CustomerAddressCreate, user: CurrentUser) -> CustomerAddress:
    require_min_role(user, "editor")
    customer = get_customer_or_404(db, customer_id)
    address = CustomerAddress(customer_id=customer.id, **payload.model_dump())
    db.add(address)
    db.flush()
    write_audit_log(
        db,
        actor=user,
        actor_type="user",
        action="customer.address.create",
        target_type="customer",
        target_id=customer_id,
        after_data=payload.model_dump(mode="json"),
    )
    db.commit()
    db.refresh(address)
    return address


def update_address(
    db: Session,
    *,
    customer_id: str,
    address_id: str,
    payload: CustomerAddressUpdate,
    user: CurrentUser,
) -> CustomerAddress:
    require_min_role(user, "editor")
    customer = get_customer_or_404(db, customer_id)
    address = next((item for item in customer.addresses if str(item.id) == address_id), None)
    if not address:
        raise not_found("Address not found")
    updates = payload.model_dump(exclude_unset=True)
    if not updates:
        raise bad_request("No fields to update")
    before = {field: getattr(address, field) for field in updates}
    for field, value in updates.items():
        setattr(address, field, value)
    write_audit_log(
        db,
        actor=user,
        actor_type="user",
        action="customer.address.update",
        target_type="customer",
        target_id=customer_id,
        before_data=before,
        after_data=updates,
    )
    db.commit()
    db.refresh(address)
    return address


def delete_address(db: Session, *, customer_id: str, address_id: str, user: CurrentUser) -> MutationResult:
    require_min_role(user, "editor")
    customer = get_customer_or_404(db, customer_id)
    address = next((item for item in customer.addresses if str(item.id) == address_id), None)
    if not address:
        raise not_found("Address not found")
    before = {"id": str(address.id), "address_type": address.address_type, "address_line": address.address_line}
    db.delete(address)
    write_audit_log(
        db,
        actor=user,
        actor_type="user",
        action="customer.address.delete",
        target_type="customer",
        target_id=customer_id,
        before_data=before,
    )
    db.commit()
    return MutationResult(status="deleted", message="Address deleted")
