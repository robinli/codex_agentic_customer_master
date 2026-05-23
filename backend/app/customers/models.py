import uuid
from datetime import datetime
from decimal import Decimal

from sqlalchemy import Boolean, DateTime, ForeignKey, Numeric, String, Text, UniqueConstraint, Uuid, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db import Base


class Customer(Base):
    __tablename__ = "customers"
    __table_args__ = (
        UniqueConstraint("customer_code", name="uq_customers_customer_code"),
        UniqueConstraint("tax_id", name="uq_customers_tax_id"),
    )

    id: Mapped[uuid.UUID] = mapped_column(Uuid, primary_key=True, default=uuid.uuid4)
    customer_code: Mapped[str] = mapped_column(String(50), nullable=False)
    customer_name: Mapped[str] = mapped_column(String(255), nullable=False, index=True)
    tax_id: Mapped[str | None] = mapped_column(String(20), nullable=True, index=True)
    customer_type: Mapped[str] = mapped_column(String(32), nullable=False)
    status: Mapped[str] = mapped_column(String(32), nullable=False, default="active")
    industry: Mapped[str | None] = mapped_column(String(100), nullable=True)
    phone: Mapped[str | None] = mapped_column(String(50), nullable=True)
    email: Mapped[str | None] = mapped_column(String(255), nullable=True)
    website: Mapped[str | None] = mapped_column(String(255), nullable=True)
    payment_terms: Mapped[str | None] = mapped_column(String(100), nullable=True)
    credit_limit: Mapped[Decimal | None] = mapped_column(Numeric(12, 2), nullable=True)
    sales_owner_id: Mapped[uuid.UUID | None] = mapped_column(Uuid, nullable=True)
    note: Mapped[str | None] = mapped_column(Text, nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())
    created_by: Mapped[uuid.UUID] = mapped_column(Uuid, nullable=False)
    updated_by: Mapped[uuid.UUID] = mapped_column(Uuid, nullable=False)

    contacts: Mapped[list["CustomerContact"]] = relationship(back_populates="customer", cascade="all, delete-orphan")
    addresses: Mapped[list["CustomerAddress"]] = relationship(back_populates="customer", cascade="all, delete-orphan")


class CustomerContact(Base):
    __tablename__ = "customer_contacts"

    id: Mapped[uuid.UUID] = mapped_column(Uuid, primary_key=True, default=uuid.uuid4)
    customer_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("customers.id", ondelete="CASCADE"), nullable=False)
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    title: Mapped[str | None] = mapped_column(String(100), nullable=True)
    phone: Mapped[str | None] = mapped_column(String(50), nullable=True)
    mobile: Mapped[str | None] = mapped_column(String(50), nullable=True)
    email: Mapped[str | None] = mapped_column(String(255), nullable=True)
    is_primary: Mapped[bool] = mapped_column(Boolean, default=False)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())

    customer: Mapped["Customer"] = relationship(back_populates="contacts")


class CustomerAddress(Base):
    __tablename__ = "customer_addresses"

    id: Mapped[uuid.UUID] = mapped_column(Uuid, primary_key=True, default=uuid.uuid4)
    customer_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("customers.id", ondelete="CASCADE"), nullable=False)
    address_type: Mapped[str] = mapped_column(String(32), nullable=False)
    postal_code: Mapped[str | None] = mapped_column(String(20), nullable=True)
    city: Mapped[str | None] = mapped_column(String(50), nullable=True)
    district: Mapped[str | None] = mapped_column(String(50), nullable=True)
    address_line: Mapped[str] = mapped_column(Text, nullable=False)
    is_primary: Mapped[bool] = mapped_column(Boolean, default=False)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())

    customer: Mapped["Customer"] = relationship(back_populates="addresses")
