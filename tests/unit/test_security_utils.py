import pytest

from core.security import get_password_hash, get_token_hash, verify_password


class TestSecurityUtils:
    def test_token_hash(self):
        token = "secret-session-token-123"
        hash1 = get_token_hash(token)
        hash2 = get_token_hash(token)

        assert hash1 == hash2
        assert len(hash1) == 64  # Длина SHA256 в hex
        assert token not in hash1  # Оригинал не должен быть виден в хеше

    @pytest.mark.parametrize(
        "password, input_pwd, expected",
        [
            ("secret123", "secret123", True),
            ("secret123", "wrong_pwd", False),
            ("!@#$%^&*", "!@#$%^&*", True),
            ("long_password_test", "short", False),
        ],
    )
    def test_password_verification(self, password, input_pwd, expected):
        hashed = get_password_hash(password)
        assert hashed.startswith("$2b$")  # Проверка формата bcrypt
        assert verify_password(input_pwd, hashed) is expected

    def test_password_salting(self):
        # Один пароль всегда дает разные хеши из-за соли
        pwd = "same_password"
        assert get_password_hash(pwd) != get_password_hash(pwd)

    @pytest.mark.parametrize("invalid_hash", ["plain_text", "short", "$2b$invalid"])
    def test_verify_password_error(self, invalid_hash):
        with pytest.raises((ValueError, Exception)):
            verify_password("any_pwd", invalid_hash)
