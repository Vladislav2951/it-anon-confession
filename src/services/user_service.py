from __future__ import annotations

import logging
from typing import TYPE_CHECKING, Optional

from pydantic import SecretStr

from core.security import get_password_hash, verify_password
from domain.dto import ChangePasswordUserInput, PatchUpdateUserInput
from domain.entities import User
from domain.enums import PermissionSlugs, SystemRole
from domain.errors import BadLoginError, ForbiddenError, NotFoundError
from domain.validators import PasswordStr


if TYPE_CHECKING:
    from pydantic import UUID7, EmailStr

    from domain.entities import Permission
    from domain.interfaces.database.uow import IDatabaseTransactionFactory

logger = logging.getLogger(__name__)


class UserService:
    def __init__(self, db_transaction_factory: IDatabaseTransactionFactory):
        self._db_transaction_factory = db_transaction_factory

    async def get_one(self, id: UUID7) -> Optional[User]:
        async with self._db_transaction_factory() as t:
            return await t.user_repo.get_one(id)

    async def get_one_by_email(self, email: EmailStr) -> Optional[User]:
        async with self._db_transaction_factory() as t:
            return await t.user_repo.get_one_by_email(email)

    async def update(self, id: UUID7, update_inp: PatchUpdateUserInput) -> User:
        async with self._db_transaction_factory() as t:
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

    async def soft_delete(self, target_user_id: UUID7, actor: User):
        if target_user_id == actor.id:
            # Пытается ли админ удалить самого себя?
            if actor.has_role(SystemRole.admin.value):
                raise ForbiddenError("Admin cannot delete another admin")

        # Удалить другого пользователя, только если есть привилегия
        elif not actor.has_permission(PermissionSlugs.users_delete_any.value):
            raise ForbiddenError("Permission denied")

        async with self._db_transaction_factory() as t:
            # Нельзя удалить администратора
            if user := await t.user_repo.get_one(target_user_id):
                if user.has_role(SystemRole.admin.value):
                    raise ForbiddenError("Cannot delete administrator")

                await t.user_repo.soft_delete(target_user_id)
                await t.session_repo.delete_all_for_user(target_user_id)

            # Уже удалён
            return

    async def get_permissions(self, user_id: UUID7) -> list[Permission]:
        async with self._db_transaction_factory() as t:
            return await t.user_repo.get_permissions(user_id)


class UserPolicy:
    @classmethod
    def can_view(cls, actor: User, target_id: UUID7) -> bool:
        return cls._can(actor, target_id, PermissionSlugs.users_view_self)

    @classmethod
    def can_view_by_email(cls, actor: User, target_email: EmailStr) -> bool:
        if actor.has_permission(PermissionSlugs.users_view_any.value):
            return True
        if actor.email == target_email and actor.has_permission(
            PermissionSlugs.users_view_self.value
        ):
            return True
        return False

    @classmethod
    def _can(cls, actor: User, target_id: UUID7, slug: PermissionSlugs) -> bool:
        if actor.has_permission(PermissionSlugs.users_view_any.value):
            return True
        if actor.id == target_id and actor.has_permission(slug.value):
            return True
        return False
