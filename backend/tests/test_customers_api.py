from fastapi.testclient import TestClient

from conftest import TEST_HEADERS, approver_headers


def test_customer_create_success(client: TestClient) -> None:
    response = client.post(
        "/api/v1/customers",
        headers=TEST_HEADERS,
        json={
            "customer_code": "CUST100",
            "customer_name": "測試客戶",
            "customer_type": "customer",
            "tax_id": "11112222",
            "status": "active",
        },
    )

    assert response.status_code == 200
    body = response.json()
    assert body["customer_code"] == "CUST100"
    assert body["tax_id"] == "11112222"


def test_customer_code_duplicate_fail(client: TestClient, created_customer_id: str) -> None:
    response = client.post(
        "/api/v1/customers",
        headers=TEST_HEADERS,
        json={
            "customer_code": "CUST001",
            "customer_name": "重複代號",
            "customer_type": "customer",
            "tax_id": "22223333",
            "status": "active",
        },
    )

    assert response.status_code == 400
    assert response.json()["detail"] == "customer_code already exists"


def test_tax_id_duplicate_fail(client: TestClient, created_customer_id: str) -> None:
    response = client.post(
        "/api/v1/customers",
        headers=TEST_HEADERS,
        json={
            "customer_code": "CUST002",
            "customer_name": "重複統編",
            "customer_type": "customer",
            "tax_id": "12345678",
            "status": "active",
        },
    )

    assert response.status_code == 400
    assert response.json()["detail"] == "tax_id already exists"


def test_update_normal_field_success(client: TestClient, created_customer_id: str) -> None:
    response = client.patch(
        f"/api/v1/customers/{created_customer_id}",
        headers=TEST_HEADERS,
        json={"phone": "02-9999-0000"},
    )

    assert response.status_code == 200
    assert response.json()["status"] == "updated"


def test_update_sensitive_field_creates_approval(client: TestClient, created_customer_id: str) -> None:
    response = client.patch(
        f"/api/v1/customers/{created_customer_id}",
        headers=TEST_HEADERS,
        json={"payment_terms": "月結60天"},
    )

    assert response.status_code == 200
    assert response.json()["status"] == "approval_required"
    assert response.json()["approval_request_id"]


def test_approve_request_applies_change(client: TestClient, created_customer_id: str) -> None:
    update_response = client.patch(
        f"/api/v1/customers/{created_customer_id}",
        headers=TEST_HEADERS,
        json={"payment_terms": "月結60天"},
    )
    approval_id = update_response.json()["approval_request_id"]

    approve_response = client.post(
        f"/api/v1/approvals/{approval_id}/approve",
        headers=approver_headers(),
    )

    assert approve_response.status_code == 200
    detail_response = client.get(f"/api/v1/customers/{created_customer_id}", headers=TEST_HEADERS)
    assert detail_response.json()["payment_terms"] == "月結60天"


def test_reject_request_does_not_apply_change(client: TestClient, created_customer_id: str) -> None:
    update_response = client.patch(
        f"/api/v1/customers/{created_customer_id}",
        headers=TEST_HEADERS,
        json={"credit_limit": "99999.00"},
    )
    approval_id = update_response.json()["approval_request_id"]

    reject_response = client.post(
        f"/api/v1/approvals/{approval_id}/reject",
        headers=approver_headers(),
        json={"comment": "資料不完整"},
    )

    assert reject_response.status_code == 200
    detail_response = client.get(f"/api/v1/customers/{created_customer_id}", headers=TEST_HEADERS)
    assert detail_response.json()["credit_limit"] is None


def test_viewer_cannot_mutate(client: TestClient) -> None:
    response = client.post(
        "/api/v1/customers",
        headers={
            "X-User-Id": "00000000-0000-0000-0000-000000000003",
            "X-User-Email": "viewer@example.com",
            "X-User-Name": "Viewer User",
            "X-User-Roles": "viewer",
        },
        json={
            "customer_code": "VIEW001",
            "customer_name": "Viewer Fail",
            "customer_type": "customer",
            "status": "active",
        },
    )

    assert response.status_code == 403


def test_editor_cannot_approve_own_request(client: TestClient, created_customer_id: str) -> None:
    update_response = client.patch(
        f"/api/v1/customers/{created_customer_id}",
        headers=TEST_HEADERS,
        json={"status": "inactive"},
    )
    approval_id = update_response.json()["approval_request_id"]

    approve_response = client.post(
        f"/api/v1/approvals/{approval_id}/approve",
        headers=TEST_HEADERS,
    )

    assert approve_response.status_code == 403
