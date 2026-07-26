from fastapi.testclient import TestClient
from datetime import timedelta
from app.security import create_access_token


TEST_EMAIL = "test@example.com"
TEST_PASSWORD = "StrongPassword123!"


def register_test_user(
    client: TestClient,
    email: str = TEST_EMAIL,
    password: str = TEST_PASSWORD,
):
    return client.post(
        "/register",
        json={
            "email": email,
            "password": password,
        },
    )


def login_test_user(
    client: TestClient,
    email: str = TEST_EMAIL,
    password: str = TEST_PASSWORD,
):
    return client.post(
        "/login",
        json={
            "email": email,
            "password": password,
        },
    )


def test_register_user(client: TestClient):
    response = register_test_user(client)

    assert response.status_code == 201

    response_data = response.json()

    assert response_data["email"] == TEST_EMAIL
    assert "id" in response_data
    assert "password" not in response_data
    assert "password_hash" not in response_data


def test_duplicate_email_is_rejected(
    client: TestClient,
):
    first_response = register_test_user(client)
    second_response = register_test_user(client)

    assert first_response.status_code == 201
    assert second_response.status_code == 409

    assert second_response.json() == {
        "detail": "Email already registered"
    }


def test_login_returns_access_token(
    client: TestClient,
):
    register_test_user(client)

    response = login_test_user(client)

    assert response.status_code == 200

    response_data = response.json()

    assert "access_token" in response_data
    assert response_data["token_type"] == "bearer"
    assert isinstance(
        response_data["access_token"],
        str,
    )
    assert len(response_data["access_token"]) > 0


def test_login_rejects_wrong_password(
    client: TestClient,
):
    register_test_user(client)

    response = login_test_user(
        client,
        password="WrongPassword123!",
    )

    assert response.status_code == 401

    assert response.json() == {
        "detail": "Invalid email or password"
    }


def test_login_rejects_unknown_email(
    client: TestClient,
):
    response = login_test_user(
        client,
        email="unknown@example.com",
    )

    assert response.status_code == 401

    assert response.json() == {
        "detail": "Invalid email or password"
    }


def test_me_requires_authentication(
    client: TestClient,
):
    response = client.get("/me")

    assert response.status_code == 401

    assert response.json() == {
        "detail": "Could not validate credentials"
    }


def test_me_returns_authenticated_user(
    client: TestClient,
):
    register_test_user(client)

    login_response = login_test_user(client)

    token = login_response.json()["access_token"]

    response = client.get(
        "/me",
        headers={
            "Authorization": f"Bearer {token}"
        },
    )

    assert response.status_code == 200

    response_data = response.json()

    assert response_data["email"] == TEST_EMAIL
    assert "id" in response_data
    assert "password_hash" not in response_data


def test_me_rejects_invalid_token(
    client: TestClient,
):
    response = client.get(
        "/me",
        headers={
            "Authorization": "Bearer invalid-token"
        },
    )

    assert response.status_code == 401

    assert response.json() == {
        "detail": "Could not validate credentials"
    }

def test_me_rejects_expired_token(
    client: TestClient,
):
    register_response = register_test_user(
        client
    )

    user_id = register_response.json()["id"]

    expired_token = create_access_token(
        data={"sub": str(user_id)},
        expires_delta=timedelta(
            minutes=-1
        ),
    )

    response = client.get(
        "/me",
        headers={
            "Authorization": (
                f"Bearer {expired_token}"
            )
        },
    )

    assert response.status_code == 401

    assert response.json() == {
        "detail": (
            "Could not validate credentials"
        )
    }


def test_user_can_change_password(
    client: TestClient,
):
    register_test_user(client)

    login_response = login_test_user(client)
    token = login_response.json()["access_token"]

    new_password = "NewStrongPassword456!"

    change_response = client.patch(
        "/account/password",
        headers={
            "Authorization": f"Bearer {token}"
        },
        json={
            "current_password": TEST_PASSWORD,
            "new_password": new_password,
        },
    )

    assert change_response.status_code == 200

    assert change_response.json() == {
        "message": "Password changed successfully"
    }

    old_login_response = login_test_user(
        client,
        password=TEST_PASSWORD,
    )

    assert old_login_response.status_code == 401

    new_login_response = login_test_user(
        client,
        password=new_password,
    )

    assert new_login_response.status_code == 200
    assert (
        "access_token"
        in new_login_response.json()
    )


def test_password_change_rejects_wrong_current_password(
    client: TestClient,
):
    register_test_user(client)

    login_response = login_test_user(client)
    token = login_response.json()["access_token"]

    response = client.patch(
        "/account/password",
        headers={
            "Authorization": f"Bearer {token}"
        },
        json={
            "current_password": (
                "IncorrectPassword123!"
            ),
            "new_password": (
                "NewStrongPassword456!"
            ),
        },
    )

    assert response.status_code == 401

    assert response.json() == {
        "detail": "Current password is incorrect"
    }


def test_password_change_rejects_same_password(
    client: TestClient,
):
    register_test_user(client)

    login_response = login_test_user(client)
    token = login_response.json()["access_token"]

    response = client.patch(
        "/account/password",
        headers={
            "Authorization": f"Bearer {token}"
        },
        json={
            "current_password": TEST_PASSWORD,
            "new_password": TEST_PASSWORD,
        },
    )

    assert response.status_code == 400

    assert response.json() == {
        "detail": (
            "New password must be different "
            "from the current password"
        )
    }


def test_user_can_delete_account(
    client: TestClient,
):
    register_test_user(client)

    login_response = login_test_user(client)
    token = login_response.json()["access_token"]

    delete_response = client.request(
        method="DELETE",
        url="/account",
        headers={
            "Authorization": f"Bearer {token}"
        },
        json={
            "current_password": TEST_PASSWORD
        },
    )

    assert delete_response.status_code == 204

    login_after_deletion = login_test_user(client)

    assert login_after_deletion.status_code == 401


def test_account_deletion_rejects_wrong_password(
    client: TestClient,
):
    register_test_user(client)

    login_response = login_test_user(client)
    token = login_response.json()["access_token"]

    response = client.request(
        method="DELETE",
        url="/account",
        headers={
            "Authorization": f"Bearer {token}"
        },
        json={
            "current_password": (
                "IncorrectPassword123!"
            )
        },
    )

    assert response.status_code == 401

    assert response.json() == {
        "detail": "Current password is incorrect"
    }

    login_after_failed_deletion = (
        login_test_user(client)
    )

    assert (
        login_after_failed_deletion.status_code
        == 200
    )