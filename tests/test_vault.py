from fastapi.testclient import TestClient
from sqlalchemy.orm import Session

from app.models import VaultItem
from tests.conftest import TestingSessionLocal


USER_ONE_EMAIL = "user1@example.com"
USER_TWO_EMAIL = "user2@example.com"
TEST_PASSWORD = "StrongPassword123!"


def register_user(
    client: TestClient,
    email: str,
):
    response = client.post(
        "/register",
        json={
            "email": email,
            "password": TEST_PASSWORD,
        },
    )

    assert response.status_code == 201

    return response


def login_user(
    client: TestClient,
    email: str,
) -> str:
    response = client.post(
        "/login",
        json={
            "email": email,
            "password": TEST_PASSWORD,
        },
    )

    assert response.status_code == 200

    return response.json()["access_token"]


def authorization_headers(
    token: str,
) -> dict[str, str]:
    return {
        "Authorization": f"Bearer {token}"
    }


def create_vault_item(
    client: TestClient,
    token: str,
    website: str = "github.com",
    username: str = "github-user",
    password: str = "GitHubPassword123!",
):
    return client.post(
        "/vault",
        headers=authorization_headers(token),
        json={
            "website": website,
            "username": username,
            "password": password,
        },
    )


def test_vault_requires_authentication(
    client: TestClient,
):
    response = client.get("/vault")

    assert response.status_code == 401


def test_create_vault_item(
    client: TestClient,
):
    register_user(client, USER_ONE_EMAIL)
    token = login_user(client, USER_ONE_EMAIL)

    response = create_vault_item(
        client=client,
        token=token,
    )

    assert response.status_code == 201

    response_data = response.json()

    assert response_data["website"] == "github.com"
    assert response_data["username"] == "github-user"
    assert "id" in response_data
    assert "created_at" in response_data

    assert "password" not in response_data
    assert "encrypted_password" not in response_data
    assert "nonce" not in response_data


def test_vault_password_is_encrypted_in_database(
    client: TestClient,
):
    plaintext_password = "SecretVaultPassword123!"

    register_user(client, USER_ONE_EMAIL)
    token = login_user(client, USER_ONE_EMAIL)

    response = create_vault_item(
        client=client,
        token=token,
        password=plaintext_password,
    )

    assert response.status_code == 201

    db: Session = TestingSessionLocal()

    try:
        stored_item = (
            db.query(VaultItem)
            .filter(
                VaultItem.id
                == response.json()["id"]
            )
            .first()
        )

        assert stored_item is not None

        assert (
            stored_item.encrypted_password
            != plaintext_password
        )

        assert (
            plaintext_password
            not in stored_item.encrypted_password
        )

        assert stored_item.nonce is not None
        assert len(stored_item.nonce) > 0

    finally:
        db.close()


def test_owner_can_read_decrypted_password(
    client: TestClient,
):
    plaintext_password = "ReadablePassword123!"

    register_user(client, USER_ONE_EMAIL)
    token = login_user(client, USER_ONE_EMAIL)

    create_response = create_vault_item(
        client=client,
        token=token,
        password=plaintext_password,
    )

    item_id = create_response.json()["id"]

    response = client.get(
        f"/vault/{item_id}",
        headers=authorization_headers(token),
    )

    assert response.status_code == 200

    response_data = response.json()

    assert (
        response_data["password"]
        == plaintext_password
    )


def test_user_only_lists_their_own_items(
    client: TestClient,
):
    register_user(client, USER_ONE_EMAIL)
    register_user(client, USER_TWO_EMAIL)

    user_one_token = login_user(
        client,
        USER_ONE_EMAIL,
    )
    user_two_token = login_user(
        client,
        USER_TWO_EMAIL,
    )

    create_vault_item(
        client=client,
        token=user_one_token,
        website="github.com",
        username="user-one-github",
    )

    create_vault_item(
        client=client,
        token=user_two_token,
        website="gmail.com",
        username="user-two-gmail",
    )

    user_one_response = client.get(
        "/vault",
        headers=authorization_headers(
            user_one_token
        ),
    )

    user_two_response = client.get(
        "/vault",
        headers=authorization_headers(
            user_two_token
        ),
    )

    assert user_one_response.status_code == 200
    assert user_two_response.status_code == 200

    user_one_items = user_one_response.json()
    user_two_items = user_two_response.json()

    assert len(user_one_items) == 1
    assert len(user_two_items) == 1

    assert (
        user_one_items[0]["website"]
        == "github.com"
    )
    assert (
        user_two_items[0]["website"]
        == "gmail.com"
    )


def test_user_cannot_read_another_users_item(
    client: TestClient,
):
    register_user(client, USER_ONE_EMAIL)
    register_user(client, USER_TWO_EMAIL)

    user_one_token = login_user(
        client,
        USER_ONE_EMAIL,
    )
    user_two_token = login_user(
        client,
        USER_TWO_EMAIL,
    )

    create_response = create_vault_item(
        client=client,
        token=user_one_token,
    )

    item_id = create_response.json()["id"]

    response = client.get(
        f"/vault/{item_id}",
        headers=authorization_headers(
            user_two_token
        ),
    )

    assert response.status_code == 404

    assert response.json() == {
        "detail": "Vault item not found"
    }


def test_user_cannot_update_another_users_item(
    client: TestClient,
):
    register_user(client, USER_ONE_EMAIL)
    register_user(client, USER_TWO_EMAIL)

    user_one_token = login_user(
        client,
        USER_ONE_EMAIL,
    )
    user_two_token = login_user(
        client,
        USER_TWO_EMAIL,
    )

    create_response = create_vault_item(
        client=client,
        token=user_one_token,
    )

    item_id = create_response.json()["id"]

    response = client.patch(
        f"/vault/{item_id}",
        headers=authorization_headers(
            user_two_token
        ),
        json={
            "password": "StolenPassword123!"
        },
    )

    assert response.status_code == 404


def test_user_cannot_delete_another_users_item(
    client: TestClient,
):
    register_user(client, USER_ONE_EMAIL)
    register_user(client, USER_TWO_EMAIL)

    user_one_token = login_user(
        client,
        USER_ONE_EMAIL,
    )
    user_two_token = login_user(
        client,
        USER_TWO_EMAIL,
    )

    create_response = create_vault_item(
        client=client,
        token=user_one_token,
    )

    item_id = create_response.json()["id"]

    response = client.delete(
        f"/vault/{item_id}",
        headers=authorization_headers(
            user_two_token
        ),
    )

    assert response.status_code == 404

    owner_response = client.get(
        f"/vault/{item_id}",
        headers=authorization_headers(
            user_one_token
        ),
    )

    assert owner_response.status_code == 200


def test_update_vault_item(
    client: TestClient,
):
    register_user(client, USER_ONE_EMAIL)
    token = login_user(client, USER_ONE_EMAIL)

    create_response = create_vault_item(
        client=client,
        token=token,
    )

    item_id = create_response.json()["id"]

    response = client.patch(
        f"/vault/{item_id}",
        headers=authorization_headers(token),
        json={
            "website": "gitlab.com",
            "password": "UpdatedPassword123!",
        },
    )

    assert response.status_code == 200

    response_data = response.json()

    assert response_data["website"] == "gitlab.com"
    assert (
        response_data["password"]
        == "UpdatedPassword123!"
    )


def test_delete_vault_item(
    client: TestClient,
):
    register_user(client, USER_ONE_EMAIL)
    token = login_user(client, USER_ONE_EMAIL)

    create_response = create_vault_item(
        client=client,
        token=token,
    )

    item_id = create_response.json()["id"]

    delete_response = client.delete(
        f"/vault/{item_id}",
        headers=authorization_headers(token),
    )

    assert delete_response.status_code == 204

    get_response = client.get(
        f"/vault/{item_id}",
        headers=authorization_headers(token),
    )

    assert get_response.status_code == 404


def test_vault_search(
    client: TestClient,
):
    register_user(client, USER_ONE_EMAIL)
    token = login_user(client, USER_ONE_EMAIL)

    create_vault_item(
        client=client,
        token=token,
        website="github.com",
        username="github-user",
    )

    create_vault_item(
        client=client,
        token=token,
        website="gmail.com",
        username="email-user",
    )

    response = client.get(
        "/vault",
        params={"search": "github"},
        headers=authorization_headers(token),
    )

    assert response.status_code == 200

    items = response.json()

    assert len(items) == 1
    assert items[0]["website"] == "github.com"


def test_account_deletion_removes_vault_items(
    client: TestClient,
):
    register_user(client, USER_ONE_EMAIL)
    token = login_user(client, USER_ONE_EMAIL)

    create_response = create_vault_item(
        client=client,
        token=token,
        website="delete-me.com",
        username="deleted-user",
        password="DeletedPassword123!",
    )

    assert create_response.status_code == 201

    item_id = create_response.json()["id"]

    delete_response = client.request(
        method="DELETE",
        url="/account",
        headers=authorization_headers(token),
        json={
            "current_password": TEST_PASSWORD
        },
    )

    assert delete_response.status_code == 204

    db: Session = TestingSessionLocal()

    try:
        deleted_item = db.get(
            VaultItem,
            item_id,
        )

        assert deleted_item is None

    finally:
        db.close()


def test_vault_pagination(
    client: TestClient,
):
    register_user(client, USER_ONE_EMAIL)
    token = login_user(client, USER_ONE_EMAIL)

    for item_number in range(5):
        response = create_vault_item(
            client=client,
            token=token,
            website=(
                f"site-{item_number}.com"
            ),
            username=(
                f"user-{item_number}"
            ),
            password=(
                f"Password{item_number}!"
            ),
        )

        assert response.status_code == 201

    first_page_response = client.get(
        "/vault",
        params={
            "offset": 0,
            "limit": 2,
            "sort_by": "website",
            "sort_order": "asc",
        },
        headers=authorization_headers(token),
    )

    second_page_response = client.get(
        "/vault",
        params={
            "offset": 2,
            "limit": 2,
            "sort_by": "website",
            "sort_order": "asc",
        },
        headers=authorization_headers(token),
    )

    assert first_page_response.status_code == 200
    assert second_page_response.status_code == 200

    first_page = first_page_response.json()
    second_page = second_page_response.json()

    assert len(first_page) == 2
    assert len(second_page) == 2

    assert (
        first_page[0]["website"]
        == "site-0.com"
    )
    assert (
        first_page[1]["website"]
        == "site-1.com"
    )
    assert (
        second_page[0]["website"]
        == "site-2.com"
    )
    assert (
        second_page[1]["website"]
        == "site-3.com"
    )


def test_vault_sorting_by_website(
    client: TestClient,
):
    register_user(client, USER_ONE_EMAIL)
    token = login_user(client, USER_ONE_EMAIL)

    create_vault_item(
        client=client,
        token=token,
        website="zebra.com",
    )

    create_vault_item(
        client=client,
        token=token,
        website="apple.com",
    )

    create_vault_item(
        client=client,
        token=token,
        website="microsoft.com",
    )

    ascending_response = client.get(
        "/vault",
        params={
            "sort_by": "website",
            "sort_order": "asc",
        },
        headers=authorization_headers(token),
    )

    descending_response = client.get(
        "/vault",
        params={
            "sort_by": "website",
            "sort_order": "desc",
        },
        headers=authorization_headers(token),
    )

    ascending_websites = [
        item["website"]
        for item in ascending_response.json()
    ]

    descending_websites = [
        item["website"]
        for item in descending_response.json()
    ]

    assert ascending_websites == [
        "apple.com",
        "microsoft.com",
        "zebra.com",
    ]

    assert descending_websites == [
        "zebra.com",
        "microsoft.com",
        "apple.com",
    ]


def test_vault_rejects_invalid_pagination(
    client: TestClient,
):
    register_user(client, USER_ONE_EMAIL)
    token = login_user(client, USER_ONE_EMAIL)

    negative_offset_response = client.get(
        "/vault",
        params={
            "offset": -1,
        },
        headers=authorization_headers(token),
    )

    excessive_limit_response = client.get(
        "/vault",
        params={
            "limit": 101,
        },
        headers=authorization_headers(token),
    )

    assert (
        negative_offset_response.status_code
        == 422
    )

    assert (
        excessive_limit_response.status_code
        == 422
    )


def test_vault_rejects_invalid_sort_field(
    client: TestClient,
):
    register_user(client, USER_ONE_EMAIL)
    token = login_user(client, USER_ONE_EMAIL)

    response = client.get(
        "/vault",
        params={
            "sort_by": "password",
        },
        headers=authorization_headers(token),
    )

    assert response.status_code == 422


def test_create_vault_item_trims_whitespace(
    client: TestClient,
):
    register_user(client, USER_ONE_EMAIL)
    token = login_user(client, USER_ONE_EMAIL)

    response = create_vault_item(
        client=client,
        token=token,
        website="   github.com   ",
        username="   github-user   ",
        password="   SecurePassword123!   ",
    )

    assert response.status_code == 201

    item_id = response.json()["id"]

    detail_response = client.get(
        f"/vault/{item_id}",
        headers=authorization_headers(token),
    )

    assert detail_response.status_code == 200

    item = detail_response.json()

    assert item["website"] == "github.com"
    assert item["username"] == "github-user"
    assert (
        item["password"]
        == "SecurePassword123!"
    )


def test_update_rejects_empty_body(
    client: TestClient,
):
    register_user(client, USER_ONE_EMAIL)
    token = login_user(client, USER_ONE_EMAIL)

    create_response = create_vault_item(
        client=client,
        token=token,
    )

    item_id = create_response.json()["id"]

    response = client.patch(
        f"/vault/{item_id}",
        headers=authorization_headers(token),
        json={},
    )

    assert response.status_code == 422


def test_vault_rejects_whitespace_only_values(
    client: TestClient,
):
    register_user(client, USER_ONE_EMAIL)
    token = login_user(client, USER_ONE_EMAIL)

    response = client.post(
        "/vault",
        headers=authorization_headers(token),
        json={
            "website": "   ",
            "username": "test-user",
            "password": "Password123!",
        },
    )

    assert response.status_code == 422