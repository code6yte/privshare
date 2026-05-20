import pytest

from crypto_utils import InvalidPassword, decrypt_bytes, encrypt_bytes, generate_token


def test_encrypt_decrypt_roundtrip():
    password = "strong test password"
    data = b"hello secure world"
    result = encrypt_bytes(data, password, iterations=1000)
    assert result.ciphertext != data
    assert decrypt_bytes(result.ciphertext, password, result.salt, result.nonce, iterations=1000) == data


def test_wrong_password_fails():
    result = encrypt_bytes(b"secret", "right-password", iterations=1000)
    with pytest.raises(InvalidPassword):
        decrypt_bytes(result.ciphertext, "wrong-password", result.salt, result.nonce, iterations=1000)


def test_token_generation():
    token = generate_token(24)
    assert isinstance(token, str)
    assert len(token) > 20
