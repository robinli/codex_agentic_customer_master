import uuid

from sqlalchemy import Select, func, or_, select
from sqlalchemy.orm import Session, selectinload

from app.customers.models import Customer


def base_customer_query() -> Select[tuple[Customer]]:
    return select(Customer).options(
        selectinload(Customer.contacts),
        selectinload(Customer.addresses),
    )


def find_customer_by_code(db: Session, customer_code: str) -> Customer | None:
    return db.scalar(select(Customer).where(Customer.customer_code == customer_code))


def find_customer_by_tax_id(db: Session, tax_id: str) -> Customer | None:
    return db.scalar(select(Customer).where(Customer.tax_id == tax_id))


def get_customer(db: Session, customer_id: str) -> Customer | None:
    return db.scalar(base_customer_query().where(Customer.id == uuid.UUID(customer_id)))


def search_customers(
    db: Session,
    *,
    q: str | None,
    status: str | None,
    customer_type: str | None,
    page: int,
    page_size: int,
) -> tuple[list[Customer], int]:
    filters = []
    if q:
        keyword = f"%{q}%"
        filters.append(
            or_(
                Customer.customer_code.ilike(keyword),
                Customer.customer_name.ilike(keyword),
                Customer.tax_id.ilike(keyword),
            )
        )
    if status:
        filters.append(Customer.status == status)
    if customer_type:
        filters.append(Customer.customer_type == customer_type)

    count_stmt = select(func.count(Customer.id))
    if filters:
        count_stmt = count_stmt.where(*filters)

    stmt = base_customer_query().order_by(Customer.updated_at.desc())
    if filters:
        stmt = stmt.where(*filters)
    stmt = stmt.offset((page - 1) * page_size).limit(page_size)
    items = list(db.scalars(stmt).unique())
    total = db.scalar(count_stmt) or 0
    return items, total
