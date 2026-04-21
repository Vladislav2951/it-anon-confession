from __future__ import annotations

import logging
from typing import TYPE_CHECKING

from pydantic import SecretStr

from core.security import get_password_hash, verify_password
from domain.dto import LoginInput, RegisterInput
from domain.entities import User
from domain.enums import SystemRole
from domain.errors import BadLoginError, ConflictError, NotFoundError


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
                raise BadLoginError(f"User {credentials.email} not found")

            if not verify_password(
                credentials.password.get_secret_value(),
                user.password_hash.get_secret_value(),
            ):
                raise BadLoginError("Incorrect password")

            return user

    async def register(self, register_inp: RegisterInput):
        async with self._db_transaction_factory() as t:
            if user := await t.user_repo.get_one_by_email(register_inp.email):
                raise ConflictError(f"User {user.email} is already registered")

            register_inp.password = SecretStr(
                get_password_hash(register_inp.password.get_secret_value())
            )
            user = User.register(
                register_inp.email,
                register_inp.password,
                register_inp.nickname,
                register_inp.bio,
            )

            user = await t.user_repo.create(user)

            role = await t.role_repo.get_one_by_name(SystemRole.user.value)
            if not role:
                raise NotFoundError(f"Role '{SystemRole.user.value}' not found")

            await t.user_repo.add_role(user.id, role.id)

            logger.info("User %s has been registered (email: %s)", user.id, user.email)
