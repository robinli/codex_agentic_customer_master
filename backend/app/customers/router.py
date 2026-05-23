from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

from app.auth.dependencies import get_current_user
from app.auth.schemas import CurrentUser
from app.common.pagination import Page
from app.customers.schemas import (
    CustomerAddressCreate,
    CustomerAddressRead,
    CustomerAddressUpdate,
    CustomerCreate,
    CustomerContactCreate,
    CustomerContactRead,
    CustomerContactUpdate,
    CustomerListItem,
    CustomerRead,
    CustomerUpdate,
    DisableCustomerRequest,
    MutationResult,
)
from app.customers.service import (
    add_address,
    add_contact,
    create_customer,
    delete_address,
    delete_contact,
    disable_customer_request,
    get_customer_or_404,
    list_customers,
    update_address,
    update_contact,
    update_customer,
)
from app.db import get_db

router = APIRouter(prefix="/customers", tags=["customers"])


@router.get("", response_model=Page[CustomerListItem])
def get_customers(
    q: str | None = Query(default=None),
    status: str | None = Query(default=None),
    customer_type: str | None = Query(default=None),
    page: int = Query(default=1, ge=1),
    page_size: int = Query(default=20, ge=1, le=100),
    db: Session = Depends(get_db),
) -> Page[CustomerListItem]:
    return list_customers(
        db,
        q=q,
        status=status,
        customer_type=customer_type,
        page=page,
        page_size=page_size,
    )


@router.get("/{customer_id}", response_model=CustomerRead)
def get_customer_detail(customer_id: str, db: Session = Depends(get_db)) -> CustomerRead:
    return get_customer_or_404(db, customer_id)


@router.post("", response_model=CustomerRead)
def create_customer_endpoint(
    payload: CustomerCreate,
    db: Session = Depends(get_db),
    current_user: CurrentUser = Depends(get_current_user),
) -> CustomerRead:
    return create_customer(db, payload=payload, user=current_user)


@router.patch("/{customer_id}", response_model=MutationResult)
def update_customer_endpoint(
    customer_id: str,
    payload: CustomerUpdate,
    db: Session = Depends(get_db),
    current_user: CurrentUser = Depends(get_current_user),
) -> MutationResult:
    return update_customer(db, customer_id=customer_id, payload=payload, user=current_user)


@router.post("/{customer_id}/disable-request", response_model=MutationResult)
def disable_customer_endpoint(
    customer_id: str,
    payload: DisableCustomerRequest,
    db: Session = Depends(get_db),
    current_user: CurrentUser = Depends(get_current_user),
) -> MutationResult:
    return disable_customer_request(db, customer_id=customer_id, reason=payload.reason, user=current_user)


@router.post("/{customer_id}/contacts", response_model=CustomerContactRead)
def create_contact_endpoint(
    customer_id: str,
    payload: CustomerContactCreate,
    db: Session = Depends(get_db),
    current_user: CurrentUser = Depends(get_current_user),
) -> CustomerContactRead:
    return add_contact(db, customer_id=customer_id, payload=payload, user=current_user)


@router.patch("/{customer_id}/contacts/{contact_id}", response_model=CustomerContactRead)
def update_contact_endpoint(
    customer_id: str,
    contact_id: str,
    payload: CustomerContactUpdate,
    db: Session = Depends(get_db),
    current_user: CurrentUser = Depends(get_current_user),
) -> CustomerContactRead:
    return update_contact(db, customer_id=customer_id, contact_id=contact_id, payload=payload, user=current_user)


@router.delete("/{customer_id}/contacts/{contact_id}", response_model=MutationResult)
def delete_contact_endpoint(
    customer_id: str,
    contact_id: str,
    db: Session = Depends(get_db),
    current_user: CurrentUser = Depends(get_current_user),
) -> MutationResult:
    return delete_contact(db, customer_id=customer_id, contact_id=contact_id, user=current_user)


@router.post("/{customer_id}/addresses", response_model=CustomerAddressRead)
def create_address_endpoint(
    customer_id: str,
    payload: CustomerAddressCreate,
    db: Session = Depends(get_db),
    current_user: CurrentUser = Depends(get_current_user),
) -> CustomerAddressRead:
    return add_address(db, customer_id=customer_id, payload=payload, user=current_user)


@router.patch("/{customer_id}/addresses/{address_id}", response_model=CustomerAddressRead)
def update_address_endpoint(
    customer_id: str,
    address_id: str,
    payload: CustomerAddressUpdate,
    db: Session = Depends(get_db),
    current_user: CurrentUser = Depends(get_current_user),
) -> CustomerAddressRead:
    return update_address(db, customer_id=customer_id, address_id=address_id, payload=payload, user=current_user)


@router.delete("/{customer_id}/addresses/{address_id}", response_model=MutationResult)
def delete_address_endpoint(
    customer_id: str,
    address_id: str,
    db: Session = Depends(get_db),
    current_user: CurrentUser = Depends(get_current_user),
) -> MutationResult:
    return delete_address(db, customer_id=customer_id, address_id=address_id, user=current_user)
