from sqlalchemy.orm import Session

from app.auth.schemas import CurrentUser
from app.customers.repository import search_customers
from app.customers.schemas import CustomerCreate, CustomerUpdate
from app.customers.service import create_customer, disable_customer_request, update_customer


def customer_search_tool(db: Session, *, query: str | None = None, tax_id: str | None = None, status: str | None = None) -> dict:
    q = tax_id or query
    items, _ = search_customers(db, q=q, status=status, customer_type=None, page=1, page_size=10)
    return {
        "items": [
            {
                "id": str(item.id),
                "customer_code": item.customer_code,
                "customer_name": item.customer_name,
                "tax_id": item.tax_id,
                "status": item.status,
            }
            for item in items
        ]
    }


def customer_create_tool(db: Session, *, payload: dict, user: CurrentUser) -> dict:
    customer = create_customer(db, payload=CustomerCreate(**payload), user=user)
    return {"id": str(customer.id), "customer_name": customer.customer_name, "status": customer.status}


def customer_update_tool(
    db: Session,
    *,
    customer_id: str,
    payload: dict,
    user: CurrentUser,
    reason: str | None = None,
) -> dict:
    result = update_customer(db, customer_id=customer_id, payload=CustomerUpdate(**payload), user=user, reason=reason)
    return result.model_dump()


def customer_disable_request_tool(db: Session, *, customer_id: str, reason: str, user: CurrentUser) -> dict:
    result = disable_customer_request(db, customer_id=customer_id, reason=reason, user=user)
    return result.model_dump()
