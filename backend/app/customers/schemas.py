from datetime import datetime
from decimal import Decimal
from typing import Any

from pydantic import BaseModel, EmailStr, Field


class CustomerContactBase(BaseModel):
    name: str
    title: str | None = None
    phone: str | None = None
    mobile: str | None = None
    email: EmailStr | None = None
    is_primary: bool = False


class CustomerContactCreate(CustomerContactBase):
    pass


class CustomerContactRead(CustomerContactBase):
    id: str
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}


class CustomerAddressBase(BaseModel):
    address_type: str
    postal_code: str | None = None
    city: str | None = None
    district: str | None = None
    address_line: str
    is_primary: bool = False


class CustomerAddressCreate(CustomerAddressBase):
    pass


class CustomerAddressRead(CustomerAddressBase):
    id: str
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}


class CustomerContactUpdate(BaseModel):
    name: str | None = None
    title: str | None = None
    phone: str | None = None
    mobile: str | None = None
    email: EmailStr | None = None
    is_primary: bool | None = None


class CustomerAddressUpdate(BaseModel):
    address_type: str | None = None
    postal_code: str | None = None
    city: str | None = None
    district: str | None = None
    address_line: str | None = None
    is_primary: bool | None = None


class CustomerCreate(BaseModel):
    customer_code: str
    customer_name: str
    customer_type: str
    tax_id: str | None = None
    status: str = "active"
    email: EmailStr | None = None
    phone: str | None = None
    website: str | None = None
    industry: str | None = None
    sales_owner_id: str | None = None
    payment_terms: str | None = None
    credit_limit: Decimal | None = None
    note: str | None = None
    contacts: list[CustomerContactCreate] = Field(default_factory=list)
    addresses: list[CustomerAddressCreate] = Field(default_factory=list)


class CustomerUpdate(BaseModel):
    customer_name: str | None = None
    tax_id: str | None = None
    phone: str | None = None
    email: EmailStr | None = None
    website: str | None = None
    note: str | None = None
    payment_terms: str | None = None
    credit_limit: Decimal | None = None
    status: str | None = None


class DisableCustomerRequest(BaseModel):
    reason: str


class CustomerRead(BaseModel):
    id: str
    customer_code: str
    customer_name: str
    tax_id: str | None
    customer_type: str
    status: str
    industry: str | None
    phone: str | None
    email: EmailStr | None
    website: str | None
    payment_terms: str | None
    credit_limit: Decimal | None
    sales_owner_id: str | None
    note: str | None
    created_at: datetime
    updated_at: datetime
    created_by: str
    updated_by: str
    contacts: list[CustomerContactRead]
    addresses: list[CustomerAddressRead]

    model_config = {"from_attributes": True}


class CustomerListItem(BaseModel):
    id: str
    customer_code: str
    customer_name: str
    tax_id: str | None
    customer_type: str
    status: str
    phone: str | None
    email: EmailStr | None
    updated_at: datetime

    model_config = {"from_attributes": True}


class MutationResult(BaseModel):
    status: str
    message: str
    approval_request_id: str | None = None
    data: dict[str, Any] | None = None
