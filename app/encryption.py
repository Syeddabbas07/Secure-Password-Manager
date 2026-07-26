import base64
import os

from cryptography.hazmat.primitives.ciphers.aead import (
    AESGCM,
)

from app.config import ENCRYPTION_KEY


def get_encryption_key() -> bytes:
    try:
        key = base64.urlsafe_b64decode(
            ENCRYPTION_KEY
        )
    except Exception as exc:
        raise RuntimeError(
            "ENCRYPTION_KEY is not valid Base64."
        ) from exc

    if len(key) not in {16, 24, 32}:
        raise RuntimeError(
            "ENCRYPTION_KEY must decode to "
            "16, 24, or 32 bytes."
        )

    return key


def encrypt_password(
    password: str,
    user_id: int,
) -> tuple[str, str]:
    key = get_encryption_key()
    aesgcm = AESGCM(key)

    nonce = os.urandom(12)

    associated_data = str(user_id).encode(
        "utf-8"
    )

    encrypted_password = aesgcm.encrypt(
        nonce,
        password.encode("utf-8"),
        associated_data,
    )

    return (
        base64.urlsafe_b64encode(
            encrypted_password
        ).decode("utf-8"),
        base64.urlsafe_b64encode(
            nonce
        ).decode("utf-8"),
    )


def decrypt_password(
    encrypted_password: str,
    nonce: str,
    user_id: int,
) -> str:
    key = get_encryption_key()
    aesgcm = AESGCM(key)

    encrypted_password_bytes = (
        base64.urlsafe_b64decode(
            encrypted_password
        )
    )

    nonce_bytes = base64.urlsafe_b64decode(
        nonce
    )

    associated_data = str(user_id).encode(
        "utf-8"
    )

    decrypted_password = aesgcm.decrypt(
        nonce_bytes,
        encrypted_password_bytes,
        associated_data,
    )

    return decrypted_password.decode("utf-8")