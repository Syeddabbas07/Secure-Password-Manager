import string

from fastapi.testclient import TestClient

from app.password_generator import generate_password


TEST_EMAIL = "generator@example.com"
TEST_PASSWORD = "StrongPassword123!"


def get_authenticated_headers(
    client: TestClient,
) -> dict[str, str]:
    register_response = client.post(
        "/register",
        json={
            "email": TEST_EMAIL,
            "password": TEST_PASSWORD,
        },
    )

    assert register_response.status_code == 201

    login_response = client.post(
        "/login",
        json={
            "email": TEST_EMAIL,
            "password": TEST_PASSWORD,
        },
    )

    assert login_response.status_code == 200

    token = login_response.json()[
        "access_token"
    ]

    return {
        "Authorization": f"Bearer {token}"
    }


def test_generate_password_function():
    password = generate_password(
        length=24,
        include_uppercase=True,
        include_lowercase=True,
        include_numbers=True,
        include_symbols=True,
    )

    assert len(password) == 24

    assert any(
        character in string.ascii_uppercase
        for character in password
    )

    assert any(
        character in string.ascii_lowercase
        for character in password
    )

    assert any(
        character in string.digits
        for character in password
    )

    assert any(
        character in string.punctuation
        for character in password
    )


def test_generate_passwords_are_different():
    password_one = generate_password(
        length=32
    )

    password_two = generate_password(
        length=32
    )

    assert password_one != password_two


def test_password_generator_requires_authentication(
    client: TestClient,
):
    response = client.post(
        "/generate-password",
        json={
            "length": 16,
            "include_uppercase": True,
            "include_lowercase": True,
            "include_numbers": True,
            "include_symbols": True,
        },
    )

    assert response.status_code == 401


def test_password_generator_endpoint(
    client: TestClient,
):
    headers = get_authenticated_headers(
        client
    )

    response = client.post(
        "/generate-password",
        headers=headers,
        json={
            "length": 20,
            "include_uppercase": True,
            "include_lowercase": True,
            "include_numbers": True,
            "include_symbols": True,
        },
    )

    assert response.status_code == 200

    generated_password = response.json()[
        "password"
    ]

    assert len(generated_password) == 20


def test_password_generator_rejects_empty_pool(
    client: TestClient,
):
    headers = get_authenticated_headers(
        client
    )

    response = client.post(
        "/generate-password",
        headers=headers,
        json={
            "length": 16,
            "include_uppercase": False,
            "include_lowercase": False,
            "include_numbers": False,
            "include_symbols": False,
        },
    )

    assert response.status_code == 400

    assert response.json() == {
        "detail": (
            "At least one character type "
            "must be enabled."
        )
    }