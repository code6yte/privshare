import os
import secrets
from dataclasses import dataclass

from cryptography.exceptions import InvalidTag
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.ciphers.aead import AESGCM
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC


SALT_BYTES = 16
NONCE_BYTES = 12
KEY_BYTES = 32
DEFAULT_ITERATIONS = 390_000


class InvalidPassword(Exception):
    """Raised when decryption fails due to wrong password or tampered ciphertext."""


@dataclass(frozen=True)
class EncryptionResult:
    ciphertext: bytes
    salt: bytes
    nonce: bytes


def generate_token(length: int = 32) -> str:
    """Generate a URL-safe token for share links."""
    return secrets.token_urlsafe(length).lower()


def derive_key(password: str, salt: bytes, iterations: int = DEFAULT_ITERATIONS) -> bytes:
    if not password or not password.strip():
        raise ValueError("Password cannot be empty")
    kdf = PBKDF2HMAC(
        algorithm=hashes.SHA256(),
        length=KEY_BYTES,
        salt=salt,
        iterations=iterations,
    )
    return kdf.derive(password.encode("utf-8"))


def encrypt_bytes(data: bytes, password: str, iterations: int = DEFAULT_ITERATIONS) -> EncryptionResult:
    salt = os.urandom(SALT_BYTES)
    nonce = os.urandom(NONCE_BYTES)
    key = derive_key(password, salt, iterations)
    aesgcm = AESGCM(key)
    ciphertext = aesgcm.encrypt(nonce, data, associated_data=None)
    return EncryptionResult(ciphertext=ciphertext, salt=salt, nonce=nonce)


def decrypt_bytes(ciphertext: bytes, password: str, salt: bytes, nonce: bytes, iterations: int = DEFAULT_ITERATIONS) -> bytes:
    key = derive_key(password, salt, iterations)
    aesgcm = AESGCM(key)
    try:
        return aesgcm.decrypt(nonce, ciphertext, associated_data=None)
    except InvalidTag as exc:
        raise InvalidPassword("Invalid password or corrupted encrypted file") from exc
