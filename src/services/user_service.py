from __future__ import annotations

import logging
from typing import TYPE_CHECKING, Optional

from pydantic import SecretStr

from core.security import get_password_hash, verify_password
from domain.dto import ChangePasswordUserInput, PatchUpdateUserInput
from domain.entities import User
from domain.enums.system_roles import SystemRole
from domain.errors import BadLoginError, ConflictError, ForbiddenError, NotFoundError
from domain.interfaces.database.filters import UserFilter
from domain.validators import PasswordStr


if TYPE_CHECKING:
    from pydantic import UUID7, EmailStr

    from domain.dto import IdentityContext
    from domain.entities import Permission
    from domain.interfaces.database.uow import IDatabaseTransactionFactory
    from services import AccessService

logger = logging.getLogger(__name__)


class UserService:
    """
    Сервис управления пользователями.

    Отвечает за бизнес-логику работы с аккаунтами: поиск, обновление данных,
    смену паролей, управление ролями и "мягкое" удаление.
    """

    def __init__(
        self,
        db_transaction_factory: IDatabaseTransactionFactory,
        access_srv: AccessService,
    ):
        self._db_transaction_factory = db_transaction_factory
        self.access_srv = access_srv

    async def get_one(self, id: UUID7) -> User:
        async with self._db_transaction_factory() as t:
            user = await t.user_repo.get_one(id)
            if not user:
                raise NotFoundError(f"User {id} not found")

            return user

    async def get_one_by_email(self, email: EmailStr) -> User:
        async with self._db_transaction_factory() as t:
            user = await t.user_repo.get_one_by_email(email)

            # await self.access_srv.check_access(
            #     identity_ctx.current_user,
            #     identity_ctx.business_element_name,
            #     identity_ctx.action,
            #     user.id if user else None,
            # )

            if not user:
                raise NotFoundError(f"User {email} not found")

            return user

    async def get_all(
        self, limit: int = 20, offset: Optional[int] = None
    ) -> tuple[list[User], int]:
        # await self.access_srv.check_access(
        #     identity_ctx.current_user,
        #     identity_ctx.business_element_name,
        #     identity_ctx.action,
        # )

        async with self._db_transaction_factory() as t:
            return await t.user_repo.get_all(None, limit, offset)

    async def update(self, id: UUID7, update_inp: PatchUpdateUserInput) -> User:
        # await self.access_srv.check_access(
        #     identity_ctx.current_user,
        #     identity_ctx.business_element_name,
        #     identity_ctx.action,
        #     id,
        # )

        async with self._db_transaction_factory() as t:
            user = await t.user_repo.get_one(id)
            if not user:
                raise NotFoundError(f"User {id} not found")

            return await t.user_repo.update(id, update_inp)

    async def change_password(
        self, id: UUID7, old_password: SecretStr, password: PasswordStr
    ):
        # await self.access_srv.check_access(
        #     identity_ctx.current_user,
        #     identity_ctx.business_element_name,
        #     identity_ctx.action,
        #     id,
        # )

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

    async def soft_delete(self, id: UUID7, current_user: User) -> None:
        #! Нельзя удалить последнего администратора
        # await self.access_srv.check_access(
        #     identity_ctx.current_user,
        #     identity_ctx.business_element_name,
        #     identity_ctx.action,
        #     id,
        # )

        async with self._db_transaction_factory() as t:
            if await t.user_repo.get_one(id):
                await t.user_repo.soft_delete(id)
                await t.session_repo.delete_all_for_user(id)

            # Уже удалён
            return None

    async def get_user_permissions(self, user_id: UUID7) -> list[Permission]:
        # await self.access_srv.check_access(
        #     identity_ctx.current_user,
        #     identity_ctx.business_element_name,
        #     identity_ctx.action,
        # )

        async with self._db_transaction_factory() as t:
            if not await t.user_repo.get_one(user_id):
                raise NotFoundError(f"User {user_id} not found")

            return await t.user_repo.get_permissions(user_id)

    async def assign_role(self, user_id: UUID7, role_id: UUID7):
        # await self.access_srv.check_access(
        #     identity_ctx.current_user,
        #     identity_ctx.business_element_name,
        #     identity_ctx.action,
        # )

        async with self._db_transaction_factory() as t:
            if not await t.user_repo.get_one(user_id):
                raise NotFoundError(f"User {user_id} not found")

            if not await t.role_repo.get_one(role_id):
                raise NotFoundError(f"Role {role_id} not found")

            await t.user_repo.assign_role(user_id, role_id)

    async def revoke_role(self, user_id: UUID7, role_id: UUID7):
        # await self.access_srv.check_access(
        #     identity_ctx.current_user,
        #     identity_ctx.business_element_name,
        #     identity_ctx.action,
        # )

        async with self._db_transaction_factory() as t:
            if not await t.user_repo.get_one(user_id):
                raise NotFoundError(f"User {user_id} not found")
            role = await t.role_repo.get_one(role_id)
            if not role:
                raise NotFoundError(f"Role {role_id} not found")

            # Запрет на снятие последнего админа
            if role.name == SystemRole.admin.value:
                admins = await t.user_repo.get_all(
                    UserFilter(roles=[SystemRole.admin.value])
                )

                # Если админ всего один
                if len(admins) == 1:
                    if admins[0].id == user_id:
                        raise ConflictError(
                            "Cannot remove the last administrator role from the system"
                        )

            await t.user_repo.revoke_role(user_id, role_id)
