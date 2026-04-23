from pydantic import BaseModel, SecretStr, ValidationError
import pytest

from domain.validators import (
    BioString,
    NameStr,
    NicknameStr,
    PasswordStr,
    TitleStr,
    sanitize_html,
)


class ValidationModel(BaseModel):
    name: NameStr = "Default"
    title: TitleStr = "Default Title"
    nickname: NicknameStr = "default_nick"
    bio: BioString = "Default bio"
    password: PasswordStr = SecretStr("password123")


class TestHtmlSanitizer:
    @pytest.mark.parametrize(
        "html_input, expected_output",
        [
            ("<script>alert('xss')</script>Hello", "Hello"),
            ("<p style='color:red'>Text</p>", "Text"),
            ("<a href='http://bad.com'>Link</a>", "Link"),
            ("<b>Clean</b> Text", "Clean Text"),
            ("Simple text", "Simple text"),
        ],
    )
    def test_sanitize_html_logic(self, html_input, expected_output):
        """Проверка удаления всех тегов и атрибутов функцией nh3."""
        assert sanitize_html(html_input) == expected_output


class TestStringValidators:
    @pytest.mark.parametrize(
        "field, value, expected",
        [
            ("name", "  John Doe  ", "John Doe"),  # strip_whitespace
            ("name", "<b>Name</b>", "Name"),  # Sanitized BeforeValidator
            ("title", "   Longer Title   ", "Longer Title"),
            ("bio", "I am a <i>developer</i>", "I am a developer"),
        ],
    )
    def test_sanitization_and_stripping(self, field, value, expected):
        """Проверка очистки HTML и пробелов для типов Name, Title, Bio."""
        m = ValidationModel(**{field: value})
        assert getattr(m, field) == expected

    @pytest.mark.parametrize(
        "nickname",
        ["user123", "admin_root", "nick-name"],
        ids=["valid", "underscore", "invalid_hyphen"],
    )
    def test_nickname_constraints(self, nickname):
        m = ValidationModel(nickname=nickname)
        assert m.nickname == nickname

    @pytest.mark.parametrize(
        "invalid_nick",
        [
            "ab",  # слишком короткий (min 3)
            "very_long_nickname_toolong",  # слишком длинный (max 16)
            "админ",  # не латиницы
            "user name",  # пробел внутри
        ],
    )
    def test_nickname_invalid(self, invalid_nick):
        with pytest.raises(ValidationError):
            ValidationModel(nickname=invalid_nick)


class TestSpecialTypes:
    def test_password_is_secret(self):
        """Пароль должен быть SecretStr и иметь мин. длину 8."""
        with pytest.raises(ValidationError):
            ValidationModel(password="short")  # < 8

        m = ValidationModel(password="valid_password")
        assert isinstance(m.password, SecretStr)
        assert m.password.get_secret_value() == "valid_password"
        assert "*****" in str(m.password)  # Не выводится в лог
