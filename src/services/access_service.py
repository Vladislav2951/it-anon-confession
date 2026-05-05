from __future__ import annotations

from typing import TYPE_CHECKING

from domain.enums import Action
from domain.errors import ForbiddenError


if TYPE_CHECKING:
    from pydantic import UUID7

    from domain.entities import Permission, User
    from domain.interfaces.database.uow import IDatabaseTransactionFactory


class AccessService:
    """
    Сервис проверки прав доступа.
    """

    def __init__(self, db_transaction_factory: IDatabaseTransactionFactory):
        self._db_transaction_factory = db_transaction_factory

    async def check_access(
        self,
        current_user: User,
        business_element_name: str,
        action: Action,
        owner_id: UUID7 | None = None,
    ) -> None:
        """
        Проверяет, имеет ли пользователь право на выполнение указанного действия.

        :param current_user: Объект текущего пользователя.
        :param business_element_name: Имя бизнес-элемента (например, 'users', 'confessions').
        :param action: Тип действия (CREATE, READ, UPDATE, DELETE).
        :param owner_id: Идентификатор владельца ресурса.

        :raises ForbiddenError: Если у пользователя недостаточно прав или действие нарушает системные правила.
        """

        async with self._db_transaction_factory() as t:
            roles = await t.role_repo.get_user_roles(current_user.id)

            role_ids = [role.id for role in roles]
            if not role_ids:
                raise ForbiddenError(f"User {current_user.id} has no roles assigned")

            permissions = await t.permission_repo.get_permissions_for_element(
                current_user.id, business_element_name
            )

            if self._is_allowed(permissions, action, current_user.id, owner_id):
                return

            raise ForbiddenError("Access denied")

    def _is_allowed(
        self,
        permissions: list[Permission],
        action: Action,
        current_user_id: UUID7 | None = None,
        owner_id: UUID7 | None = None,
    ) -> bool:
        for perm in permissions:
            # CRUD all
            if action == Action.CREATE:
                has_permission = perm.create_permission
            elif action == Action.READ:
                has_permission = perm.read_permission
            elif action == Action.UPDATE:
                has_permission = perm.update_permission
            elif action == Action.DELETE:
                has_permission = perm.delete_permission

            if has_permission:
                return True

            # RUD own
            if current_user_id and owner_id and current_user_id == owner_id:
                if action == Action.READ:
                    has_permission = perm.read_own_permission
                elif action == Action.UPDATE:
                    has_permission = perm.update_own_permission
                elif action == Action.DELETE:
                    has_permission = perm.delete_own_permission

                return has_permission

        return False
