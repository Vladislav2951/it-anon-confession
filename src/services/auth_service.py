from __future__ import annotations

from typing import TYPE_CHECKING

from uuid_extensions import uuid7  # type: ignore[import-untyped]

from core.security import verify_password
from domain.dto import LoginInput
from domain.entities import User
from domain.errors import BadLogin


if TYPE_CHECKING:
    from domain.interfaces.database.uow import IDatabaseUoWFactory


class AuthService:
    def __init__(self, db_uow_factory: IDatabaseUoWFactory):
        self._db_uow_factory = db_uow_factory

    async def login(self, credentials: LoginInput) -> User:
        uow = self._db_uow_factory()
        user = await uow.user_repo.get_one_by_email(credentials.email)
        if not user:
            raise BadLogin(f"User {credentials.email} not found")

        if not verify_password(
            credentials.password.get_secret_value(), user.password_hash.get_secret_value()
        ):
            raise BadLogin("Incorrect password")

        return user
