from __future__ import annotations

from typing import TYPE_CHECKING

from uuid_extensions import uuid7  # type: ignore[import-untyped]

from core.security import verify_password
from domain.dto import LoginInput
from domain.entities import User


class AuthService:
    def login(self, credentials: LoginInput) -> User:
        # TODO get user
        user = User(
            id=uuid7(),
            email="example@site.ru",
            password_hash=credentials.password,  # !
            first_name="Гадя",
            father_name="Петрович",
            last_name="Хренова",
        )

        # TODO verify
        # bool(login == tmp_login and verify_password(password, tmp_hash))
        return user
