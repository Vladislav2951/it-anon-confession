from __future__ import annotations

import logging
from typing import TYPE_CHECKING, Optional

from pydantic import SecretStr

from core.security import get_password_hash, verify_password
from domain.dto import ChangePasswordUserInput, PatchUpdateUserInput
from domain.entities import User
from domain.enums.system_roles import SystemRole
from domain.errors import BadLoginError, ConflictError, NotFoundError
from domain.interfaces.database.filters import UserFilter
from domain.validators import Identifier, PasswordStr


if TYPE_CHECKING:
    from pydantic import UUID7, EmailStr

    from domain.entities import Permission
    from domain.interfaces.database.uow import IDatabaseTransactionFactory
    from services import AccessService

logger = logging.getLogger(__name__)


class UserService:
    """
    Сервис управления пользователями.
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
            if not user:
                raise NotFoundError(f"User {email} not found")

            return user

    async def get_all(
        self, limit: int = 20, offset: Optional[int] = None
    ) -> tuple[list[User], int]:
        async with self._db_transaction_factory() as t:
            if count := await t.user_repo.count():
                users = await t.user_repo.get_all(None, limit, offset)
                return users, count
            else:
                return [], 0

    async def update(self, id: UUID7, update_inp: PatchUpdateUserInput) -> User:
        async with self._db_transaction_factory() as t:
            user = await t.user_repo.get_one(id)
            if not user:
                raise NotFoundError(f"User {id} not found")

            return await t.user_repo.update(id, update_inp)

    async def change_password(
        self, id: UUID7, old_password: SecretStr, password: PasswordStr
    ):
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
        async with self._db_transaction_factory() as t:
            if await t.user_repo.get_one(id):
                if current_user.id == id:
                    # Нельзя удалить последнего администратора
                    roles = await t.role_repo.get_user_roles(id)
                    if any(r.name == SystemRole.admin.value for r in roles):
                        admins_count = await t.user_repo.count(
                            UserFilter(roles=[SystemRole.admin.value])
                        )
                        if admins_count == 1:
                            raise ConflictError("System requires at least one admin")

                        logger.warning("Administrator %s is going to be deleted", id)

                await t.user_repo.soft_delete(id)
                await t.session_repo.delete_all_for_user(id)

            # Уже удалён
            return None

    async def get_user_permissions(self, user_id: UUID7) -> list[Permission]:
        async with self._db_transaction_factory() as t:
            if not await t.user_repo.get_one(user_id):
                raise NotFoundError(f"User {user_id} not found")

            return await t.user_repo.get_permissions(user_id)

    async def assign_role(self, user_id: UUID7, role_id: UUID7):
        async with self._db_transaction_factory() as t:
            if not await t.user_repo.get_one(user_id):
                raise NotFoundError(f"User {user_id} not found")

            if not await t.role_repo.get_one(role_id):
                raise NotFoundError(f"Role {role_id} not found")

            await t.user_repo.assign_role(user_id, role_id)

    async def revoke_role(self, user_id: UUID7, role_id: UUID7):
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

    async def get_owner_id(self, identifier: Identifier) -> Optional[UUID7]:
        if isinstance(identifier, str):
            async with self._db_transaction_factory() as t:
                return await t.user_repo.get_id_by_email(identifier)
        else:
            return identifier
