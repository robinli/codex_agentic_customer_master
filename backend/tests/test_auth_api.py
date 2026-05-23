from fastapi.testclient import TestClient


def test_login_success(client: TestClient) -> None:
    response = client.post(
        "/api/v1/auth/login",
        json={"email": "editor@example.com", "password": "editor1234"},
    )

    assert response.status_code == 200
    body = response.json()
    assert body["access_token"]
    assert body["user"]["email"] == "editor@example.com"


def test_login_fail(client: TestClient) -> None:
    response = client.post(
        "/api/v1/auth/login",
        json={"email": "editor@example.com", "password": "wrong-password"},
    )

    assert response.status_code == 403


def test_me_with_bearer_token(client: TestClient) -> None:
    login_response = client.post(
        "/api/v1/auth/login",
        json={"email": "approver@example.com", "password": "approver1234"},
    )
    token = login_response.json()["access_token"]

    response = client.get(
        "/api/v1/me",
        headers={"Authorization": f"Bearer {token}"},
    )

    assert response.status_code == 200
    assert response.json()["roles"] == ["approver"]
