import uuid
from collections.abc import Generator

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import Session, sessionmaker
from sqlalchemy.pool import StaticPool

from app.agent.models import AgentMessage, AgentSession
from app.approvals.models import ApprovalRequest
from app.audit.models import AuditLog
from app.customers.models import Customer, CustomerAddress, CustomerContact
from app.db import Base, get_db
from app.main import create_app


TEST_HEADERS = {
    "X-User-Id": "00000000-0000-0000-0000-000000000001",
    "X-User-Email": "editor@example.com",
    "X-User-Name": "Editor User",
    "X-User-Roles": "editor",
}


@pytest.fixture
def db_session() -> Generator[Session, None, None]:
    engine = create_engine(
        "sqlite+pysqlite:///:memory:",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
        future=True,
    )
    TestingSessionLocal = sessionmaker(bind=engine, autoflush=False, autocommit=False, future=True)
    Base.metadata.create_all(bind=engine)
    session = TestingSessionLocal()
    try:
        yield session
    finally:
        session.close()


@pytest.fixture
def client(db_session: Session) -> Generator[TestClient, None, None]:
    app = create_app()

    def override_get_db() -> Generator[Session, None, None]:
        yield db_session

    app.dependency_overrides[get_db] = override_get_db
    with TestClient(app) as test_client:
        yield test_client


@pytest.fixture
def created_customer_id(client: TestClient) -> str:
    response = client.post(
        "/api/v1/customers",
        headers=TEST_HEADERS,
        json={
            "customer_code": "CUST001",
            "customer_name": "大明有限公司",
            "customer_type": "customer",
            "tax_id": "12345678",
            "status": "active",
            "phone": "02-1234-5678",
        },
    )
    return response.json()["id"]


def approver_headers(user_id: str = "00000000-0000-0000-0000-000000000002") -> dict[str, str]:
    return {
        "X-User-Id": user_id,
        "X-User-Email": "approver@example.com",
        "X-User-Name": "Approver User",
        "X-User-Roles": "approver",
    }

