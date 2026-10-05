import pytest
from app.core.crypto import encrypt_value, decrypt_value, mask_key

def test_encryption_roundtrip():
    secret = "sk-ant-api03-samplekey1234567890abcdef"
    encrypted = encrypt_value(secret)
    assert encrypted != secret
    assert isinstance(encrypted, str)

    decrypted = decrypt_value(encrypted)
    assert decrypted == secret

def test_mask_key():
    assert mask_key("sk-12345678") == "****...5678"
    assert mask_key("abcd") == "****"
    assert mask_key("") == "****"
