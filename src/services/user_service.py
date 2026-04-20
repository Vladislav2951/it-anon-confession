from __future__ import annotations

import logging
from typing import TYPE_CHECKING, Optional

from domain.entities import User
from domain.enums import PermissionSlugs, SystemRole
from domain.errors import ForbiddenError


if TYPE_CHECKING:
    from pydantic import UUID7, EmailStr

logger = logging.getLogger(__name__)


if TYPE_CHECKING:
    from domain.interfaces.database.uow import IDatabaseTransactionFactory


class UserService:
    def __init__(self, db_transaction_factory: IDatabaseTransactionFactory):
        self._db_transaction_factory = db_transaction_factory

    async def get_one(self, id: UUID7) -> Optional[User]:
        async with self._db_transaction_factory() as t:
            return await t.user_repo.get_one(id)

    async def get_one_by_email(self, email: EmailStr) -> Optional[User]:
        async with self._db_transaction_factory() as t:
            return await t.user_repo.get_one_by_email(email)

    async def soft_delete(self, target_user_id: UUID7, actor: User):
        if target_user_id == actor.id:
            # Пытается ли админ удалить самого себя?
            if actor.has_role(SystemRole.admin.value):
                raise ForbiddenError("Admin cannot delete another admin")

        # Удалить другого пользователя, только если есть привилегия
        elif not actor.has_permission(PermissionSlugs.users_delete.value):
            raise ForbiddenError("Permission denied")

        async with self._db_transaction_factory() as t:
            # Нельзя удалить администратора
            if user := await t.user_repo.get_one(target_user_id, with_roles=True):
                if user.has_role(SystemRole.admin.value):
                    raise ForbiddenError("Cannot delete administrator")

                await t.user_repo.soft_delete(target_user_id)
                await t.session_repo.delete_all_for_user(target_user_id)

            # Уже удалён
            return
