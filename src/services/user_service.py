from __future__ import annotations

import logging
from typing import TYPE_CHECKING, Optional

from pydantic import SecretStr

from core.security import get_password_hash, verify_password
from domain.dto import ChangePasswordUserInput, PatchUpdateUserInput
from domain.entities import User
from domain.errors import BadLoginError, NotFoundError
from domain.validators import PasswordStr


if TYPE_CHECKING:
    from pydantic import UUID7, EmailStr

    from domain.dto import IdentityContext
    from domain.interfaces.database.uow import IDatabaseTransactionFactory
    from services import AccessService

logger = logging.getLogger(__name__)


class UserService:
    def __init__(
        self,
        db_transaction_factory: IDatabaseTransactionFactory,
        access_srv: AccessService,
    ):
        self._db_transaction_factory = db_transaction_factory
        self.access_srv = access_srv

    async def get_one(self, id: UUID7, identity_ctx: IdentityContext) -> Optional[User]:
        await self.access_srv.check_access(
            identity_ctx.current_user,
            identity_ctx.business_element_name,
            identity_ctx.action,
            id,
        )

        async with self._db_transaction_factory() as t:
            return await t.user_repo.get_one(id)

    async def get_one_by_email(
        self, email: EmailStr, identity_ctx: IdentityContext
    ) -> Optional[User]:
        async with self._db_transaction_factory() as t:
            user = await t.user_repo.get_one_by_email(email)

            await self.access_srv.check_access(
                identity_ctx.current_user,
                identity_ctx.business_element_name,
                identity_ctx.action,
                user.id if user else None,
            )

            return user

    async def update(
        self, id: UUID7, update_inp: PatchUpdateUserInput, identity_ctx: IdentityContext
    ) -> User:
        await self.access_srv.check_access(
            identity_ctx.current_user,
            identity_ctx.business_element_name,
            identity_ctx.action,
            id,
        )

        async with self._db_transaction_factory() as t:
            user = await t.user_repo.get_one(id)
            if not user:
                raise NotFoundError(f"User {id} not found")

            return await t.user_repo.update(id, update_inp)

    async def change_password(
        self,
        id: UUID7,
        old_password: SecretStr,
        password: PasswordStr,
        identity_ctx: IdentityContext,
    ):
        await self.access_srv.check_access(
            identity_ctx.current_user,
            identity_ctx.business_element_name,
            identity_ctx.action,
            id,
        )

        async with self._db_transaction_factory() as t:
            user = await t.user_repo.get_one(id)
            if not user:
                raise NotFoundError(f"User {id} not found")

            if not verify_password(
                old_password.get_secret_value(), user.password_hash.get_secret_value()
            ):
                raise BadLoginError(f"Incorrect current password")

            new_password_hash = SecretStr(get_password_hash(password.get_secret_value()))

            _ = await t.user_repo.update(
                id, ChangePasswordUserInput(password_hash=new_password_hash)
            )

    async def soft_delete(self, id: UUID7, identity_ctx: IdentityContext):
        # Нельзя удалить администратора
        await self.access_srv.check_access(
            identity_ctx.current_user,
            identity_ctx.business_element_name,
            identity_ctx.action,
            id,
        )

        async with self._db_transaction_factory() as t:
            if await t.user_repo.get_one(id):
                await t.user_repo.soft_delete(id)
                await t.session_repo.delete_all_for_user(id)

            # Уже удалён
            return
