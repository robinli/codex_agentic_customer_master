import uuid
from decimal import Decimal

from sqlalchemy.orm import Session

from app.customers.models import Customer, CustomerAddress, CustomerContact


def seed_customers(db: Session) -> None:
    if db.query(Customer).count() > 0:
        return

    editor_id = uuid.UUID("00000000-0000-0000-0000-000000000001")
    customers = [
        Customer(
            customer_code="CUST001",
            customer_name="大明有限公司",
            tax_id="12345678",
            customer_type="customer",
            status="active",
            phone="02-1234-5678",
            email="contact@demo-one.test",
            payment_terms="月結30天",
            credit_limit=Decimal("100000.00"),
            created_by=editor_id,
            updated_by=editor_id,
            contacts=[CustomerContact(name="王小明", phone="02-1234-5678", email="ming@demo-one.test", is_primary=True)],
            addresses=[CustomerAddress(address_type="office", city="Taipei", district="Xinyi", address_line="松仁路 1 號", is_primary=True)],
        ),
        Customer(
            customer_code="DIST001",
            customer_name="北區經銷股份有限公司",
            tax_id="22345678",
            customer_type="distributor",
            status="active",
            created_by=editor_id,
            updated_by=editor_id,
        ),
        Customer(
            customer_code="INACT001",
            customer_name="停用測試客戶",
            tax_id="32345678",
            customer_type="customer",
            status="inactive",
            created_by=editor_id,
            updated_by=editor_id,
        ),
        Customer(
            customer_code="MULTI001",
            customer_name="多聯絡人企業",
            tax_id="42345678",
            customer_type="partner",
            status="active",
            created_by=editor_id,
            updated_by=editor_id,
            contacts=[
                CustomerContact(name="陳經理", phone="02-2222-2222", is_primary=True),
                CustomerContact(name="林專員", mobile="0912-000-000"),
            ],
        ),
        Customer(
            customer_code="ADDR001",
            customer_name="多地址貿易有限公司",
            tax_id="52345678",
            customer_type="vendor",
            status="active",
            created_by=editor_id,
            updated_by=editor_id,
            addresses=[
                CustomerAddress(address_type="billing", city="Taichung", district="West", address_line="台灣大道 1 號", is_primary=True),
                CustomerAddress(address_type="shipping", city="Kaohsiung", district="Lingya", address_line="中山路 88 號"),
            ],
        ),
    ]
    db.add_all(customers)
    db.commit()
