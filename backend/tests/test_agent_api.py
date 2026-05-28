from fastapi.testclient import TestClient

from conftest import TEST_HEADERS


def create_session(client: TestClient, title: str = "agent") -> str:
    response = client.post("/api/v1/agent/sessions", headers=TEST_HEADERS, json={"title": title})
    return response.json()["id"]


def test_agent_tool_customer_search_success(client: TestClient, created_customer_id: str) -> None:
    session_id = create_session(client, "search")

    response = client.post(
        f"/api/v1/agent/sessions/{session_id}/messages",
        headers=TEST_HEADERS,
        json={"message": "幫我查詢統編 12345678 的客戶"},
    )

    assert response.status_code == 200
    body = response.json()
    assert body["tool_calls"][0]["tool_name"] == "customer.search"
    assert len(body["data"]["items"]) == 1


def test_agent_tool_customer_update_sensitive_field_creates_approval(client: TestClient, created_customer_id: str) -> None:
    session_id = create_session(client, "update")

    preview_response = client.post(
        f"/api/v1/agent/sessions/{session_id}/messages",
        headers=TEST_HEADERS,
        json={"message": "把統編 12345678 的付款條件改成 月結 60 天，原因是客戶重新議約"},
    )

    assert preview_response.status_code == 200
    assert preview_response.json()["data"]["pending_confirmation"] is True
    assert preview_response.json()["tool_calls"] == []

    confirm_response = client.post(
        f"/api/v1/agent/sessions/{session_id}/messages",
        headers=TEST_HEADERS,
        json={"message": "確認"},
    )

    assert confirm_response.status_code == 200
    assert confirm_response.json()["tool_calls"][0]["tool_name"] == "customer.update"
    assert confirm_response.json()["data"]["status"] == "approval_required"


def test_agent_tool_customer_update_name_success(client: TestClient, created_customer_id: str) -> None:
    session_id = create_session(client, "update-name")

    response = client.post(
        f"/api/v1/agent/sessions/{session_id}/messages",
        headers=TEST_HEADERS,
        json={"message": "將統編 12345678 的客戶名稱改為 CKK"},
    )

    assert response.status_code == 200
    assert response.json()["tool_calls"][0]["tool_name"] == "customer.update"
    assert response.json()["data"]["status"] == "updated"

    customer_response = client.get(f"/api/v1/customers/{created_customer_id}", headers=TEST_HEADERS)
    assert customer_response.json()["customer_name"] == "CKK"


def test_agent_tool_customer_update_phone_by_name_success(client: TestClient, created_customer_id: str) -> None:
    session_id = create_session(client, "update-phone-name")

    response = client.post(
        f"/api/v1/agent/sessions/{session_id}/messages",
        headers=TEST_HEADERS,
        json={"message": "把大明有限公司電話改成 07-2235803"},
    )

    assert response.status_code == 200
    assert response.json()["tool_calls"][0]["tool_name"] == "customer.update"
    assert response.json()["data"]["status"] == "updated"

    customer_response = client.get(f"/api/v1/customers/{created_customer_id}", headers=TEST_HEADERS)
    assert customer_response.json()["phone"] == "07-2235803"


def test_agent_search_multiple_results_asks_for_clarification(client: TestClient, created_customer_id: str) -> None:
    client.post(
        "/api/v1/customers",
        headers=TEST_HEADERS,
        json={
            "customer_code": "CUST002",
            "customer_name": "大明貿易股份有限公司",
            "customer_type": "customer",
            "tax_id": "22334455",
            "status": "active",
        },
    )
    session_id = create_session(client, "ambiguous-search")

    response = client.post(
        f"/api/v1/agent/sessions/{session_id}/messages",
        headers=TEST_HEADERS,
        json={"message": "查詢大明"},
    )

    assert response.status_code == 200
    assert "查到多筆客戶" in response.json()["message"]
    assert len(response.json()["data"]["items"]) == 2


def test_agent_create_customer_with_labeled_name_and_tax_id(client: TestClient) -> None:
    session_id = create_session(client, "create-labeled-customer")

    response = client.post(
        f"/api/v1/agent/sessions/{session_id}/messages",
        headers=TEST_HEADERS,
        json={"message": "新增客戶 名稱:大王紅茶 統編:99990000"},
    )

    assert response.status_code == 200
    body = response.json()
    assert body["tool_calls"][0]["tool_name"] == "customer.create"
    assert body["tool_calls"][0]["input"]["customer_name"] == "大王紅茶"
    assert body["tool_calls"][0]["input"]["tax_id"] == "99990000"
    assert body["data"]["customer_name"] == "大王紅茶"


def test_agent_sensitive_change_without_reason_requests_reason(client: TestClient, created_customer_id: str) -> None:
    session_id = create_session(client, "missing-reason")

    response = client.post(
        f"/api/v1/agent/sessions/{session_id}/messages",
        headers=TEST_HEADERS,
        json={"message": "把統編 12345678 的付款條件改成 月結 60 天"},
    )

    assert response.status_code == 200
    assert "需要提供原因" in response.json()["message"]
    assert response.json()["tool_calls"] == []


def test_agent_disable_customer_requires_reason_then_confirmation(client: TestClient, created_customer_id: str) -> None:
    session_id = create_session(client, "disable")

    reason_response = client.post(
        f"/api/v1/agent/sessions/{session_id}/messages",
        headers=TEST_HEADERS,
        json={"message": "停用統編 12345678 的客戶"},
    )

    assert reason_response.status_code == 200
    assert "請先提供原因" in reason_response.json()["message"]

    preview_response = client.post(
        f"/api/v1/agent/sessions/{session_id}/messages",
        headers=TEST_HEADERS,
        json={"message": "停用統編 12345678 的客戶，原因是已結束合作"},
    )

    assert preview_response.status_code == 200
    assert preview_response.json()["data"]["pending_confirmation"] is True

    confirm_response = client.post(
        f"/api/v1/agent/sessions/{session_id}/messages",
        headers=TEST_HEADERS,
        json={"message": "確認"},
    )

    assert confirm_response.status_code == 200
    assert confirm_response.json()["tool_calls"][0]["tool_name"] == "customer.disable_request"
    assert confirm_response.json()["data"]["status"] == "approval_required"
