from __future__ import annotations

import logging
from typing import TYPE_CHECKING

from pydantic import SecretStr

from core.security import get_password_hash, verify_password
from domain.dto import LoginInput, RegisterInput
from domain.entities import User
from domain.errors import BadLogin, ConflictError


logger = logging.getLogger(__name__)


if TYPE_CHECKING:
    from domain.interfaces.database.uow import IDatabaseTransactionFactory


class AuthService:
    def __init__(self, db_transaction_factory: IDatabaseTransactionFactory):
        self._db_transaction_factory = db_transaction_factory

    async def login(self, credentials: LoginInput) -> User:
        async with self._db_transaction_factory() as t:
            user = await t.user_repo.get_one_by_email(credentials.email)
            if not user:
                raise BadLogin(f"User {credentials.email} not found")

            if not verify_password(
                credentials.password.get_secret_value(),
                user.password_hash.get_secret_value(),
            ):
                raise BadLogin("Incorrect password")

            return user

    async def register(self, register: RegisterInput):
        async with self._db_transaction_factory() as t:
            if user := await t.user_repo.get_one_by_email(register.email):
                raise ConflictError(f"User {user.email} is already registered")

            register.password = SecretStr(
                get_password_hash(register.password.get_secret_value())
            )

            user = await t.user_repo.create(register)

            logger.info("User %s has been registered (email: %s)", user.id, user.email)
