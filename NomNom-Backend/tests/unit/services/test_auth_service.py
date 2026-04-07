from src.services.auth_service import create_token, decode_token, hash_password, verify_password


def test_hash_and_verify_password():
    hashed = hash_password("mypassword")
    assert hashed != "mypassword"
    assert verify_password("mypassword", hashed) is True
    assert verify_password("wrongpassword", hashed) is False


def test_create_and_decode_token():
    token = create_token(user_id=42)
    payload = decode_token(token)
    assert payload["sub"] == "42"
    assert "exp" in payload
    assert "iat" in payload
