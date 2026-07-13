import base64
import os
import secrets

from cryptography.hazmat.primitives.ciphers.aead import AESGCM
from dotenv import load_dotenv

load_dotenv()

encoded_encryption_key = os.getenv("ENCRYPTION_KEY")

if not encoded_encryption_key:
    raise RuntimeError(
        "ENCRYPTION_KEY is missing. Add it to the .env file."
    )

try:
    encryption_key = base64.urlsafe_b64decode(
        encoded_encryption_key
    )
except Exception as exc:
    raise RuntimeError(
        "ENCRYPTION_KEY must be valid URL-safe Base64."
    ) from exc

if len(encryption_key) != 32:
    raise RuntimeError(
        "ENCRYPTION_KEY must decode to exactly 32 bytes."
    )

aesgcm = AESGCM(encryption_key)


def encrypt_password(
    password: str,
    user_id: int,
) -> tuple[str, str]:
    nonce = secrets.token_bytes(12)
    associated_data = str(user_id).encode("utf-8")

    ciphertext = aesgcm.encrypt(
        nonce,
        password.encode("utf-8"),
        associated_data,
    )

    encoded_ciphertext = base64.urlsafe_b64encode(
        ciphertext
    ).decode("utf-8")

    encoded_nonce = base64.urlsafe_b64encode(
        nonce
    ).decode("utf-8")

    return encoded_ciphertext, encoded_nonce


def decrypt_password(
    encrypted_password: str,
    nonce: str,
    user_id: int,
) -> str:
    ciphertext_bytes = base64.urlsafe_b64decode(
        encrypted_password
    )

    nonce_bytes = base64.urlsafe_b64decode(nonce)
    associated_data = str(user_id).encode("utf-8")

    plaintext = aesgcm.decrypt(
        nonce_bytes,
        ciphertext_bytes,
        associated_data,
    )

    return plaintext.decode("utf-8")