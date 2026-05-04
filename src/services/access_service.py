from __future__ import annotations

from typing import TYPE_CHECKING

from domain.enums import Action
from domain.errors import ForbiddenError


if TYPE_CHECKING:
    from domain.entities import Permission, User
    from domain.interfaces.database.uow import IDatabaseTransactionFactory


class AccessService:
    """
    Сервис проверки прав доступа.
    """

    def __init__(self, db_transaction_factory: IDatabaseTransactionFactory):
        self._db_transaction_factory = db_transaction_factory

    async def check_access(
        self, user: User, business_element_name: str, action: Action
    ) -> None:
        """
        Проверяет, имеет ли пользователь право на выполнение указанного действия.

        :param user: Объект текущего пользователя.
        :param business_element_name: Имя бизнес-элемента (например, 'users', 'confessions').
        :param action: Тип действия (CREATE, READ, UPDATE, DELETE).

        :raises ForbiddenError: Если у пользователя недостаточно прав или действие нарушает системные правила.
        """

        async with self._db_transaction_factory() as t:
            roles = await t.role_repo.get_user_roles(user.id)

            role_ids = [role.id for role in roles]
            if not role_ids:
                raise ForbiddenError(f"User {user.id} has no roles assigned")

            permissions = await t.permission_repo.get_permissions_for_element(
                user.id, business_element_name
            )

            if self._is_allowed(permissions=permissions, action=action):
                #  Нельзя удалить последнего администратора
                # if (
                #     action == Action.DELETE
                #     and resource_owner_id == user.id
                #     and any(r.name == SystemRole.admin.value for r in roles)
                # ):
                #     admins = await t.user_repo.get_all(
                #         UserFilter(roles=[SystemRole.admin.value])
                #     )
                #     if len(admins) == 1:
                #         raise ForbiddenError("System requires at least one admin")

                return

            raise ForbiddenError("Access denied")

    def _is_allowed(self, *, permissions: list[Permission], action: Action) -> bool:
        for perm in permissions:
            if action == Action.CREATE:
                has_permission = perm.create_permission
            elif action == Action.READ:
                has_permission = perm.read_permission
            elif action == Action.UPDATE:
                has_permission = perm.update_permission
            elif action == Action.DELETE:
                has_permission = perm.delete_permission

            return has_permission

        return False
