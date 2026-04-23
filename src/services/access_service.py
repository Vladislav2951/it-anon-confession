from __future__ import annotations

from typing import TYPE_CHECKING, Optional

from domain.enums import Action, SystemRole
from domain.errors import ForbiddenError
from domain.interfaces.database.filters import UserFilter
from domain.interfaces.database.uow import IDatabaseTransactionFactory


if TYPE_CHECKING:
    from pydantic import UUID7

    from domain.entities import Permission, User


class AccessService:
    """
    Сервис проверки прав доступа.

    Реализует логику авторизации на основе RBAC (Role-Based Access Control).
    Проверяет наличие необходимых разрешений (Permissions) у пользователя
    для выполнения действий над бизнес-элементами.
    """

    def __init__(self, db_transaction_factory: IDatabaseTransactionFactory):
        self._db_transaction_factory = db_transaction_factory

    async def check_access(
        self,
        user: Optional[User],
        business_element_name: str,
        action: Action,
        resource_owner_id: Optional[UUID7] = None,
    ) -> None:
        """
        Проверяет, имеет ли пользователь право на выполнение указанного действия.

        Метод выполняет последовательную проверку:
        1. Наличие активного пользователя.
        2. Получение всех ролей и связанных с ними разрешений для конкретного бизнес-элемента.
        3. Проверка специфических правил (доступ ко всем объектам или только к своим).
        4. Запрет на удаление последнего администратора в системе.

        :param user: Объект текущего пользователя.
        :param business_element_name: Имя бизнес-элемента (например, 'users', 'confessions').
        :param action: Тип действия (CREATE, READ, UPDATE, DELETE).
        :param resource_owner_id: ID владельца ресурса (необязательно, используется для проверки доступа к своим записям).

        :raises ForbiddenError: Если у пользователя недостаточно прав или действие нарушает системные правила.
        :raises RuntimeError: Если вызов произведен некорректно (для неактивного пользователя).
        """

        if business_element_name == "__system__":
            return

        if not user or (user and not user.is_active()):
            raise RuntimeError("This code should not be reached")

        async with self._db_transaction_factory() as t:
            roles = await t.role_repo.get_user_roles(user.id)

            role_ids = [role.id for role in roles]
            if not role_ids:
                raise ForbiddenError(f"User {user.id} has no roles assigned")

            permissions = await t.permission_repo.get_permissions_for_element(
                user.id, business_element_name
            )

            if self._is_allowed(
                permissions=permissions,
                user_id=user.id,
                action=action,
                resource_owner_id=resource_owner_id,
            ):
                #  Нельзя удалить последнего администратора
                if (
                    action == Action.DELETE
                    and resource_owner_id == user.id
                    and any(r.name == SystemRole.admin.value for r in roles)
                ):
                    admins = await t.user_repo.get_all(
                        UserFilter(roles=[SystemRole.admin.value])
                    )
                    if len(admins) == 1:
                        raise ForbiddenError("System requires at least one admin")

                return

            raise ForbiddenError("Access denied")

    def _is_allowed(
        self,
        *,
        permissions: list[Permission],
        user_id: UUID7,
        action: Action,
        resource_owner_id: UUID7 | None,
    ) -> bool:
        own_permission_map = {
            Action.READ: "read_permission",
            Action.CREATE: "create_permission",
            Action.UPDATE: "update_permission",
            Action.DELETE: "delete_permission",
        }

        all_permission_map = {
            Action.READ: "read_all_permission",
            Action.CREATE: None,
            Action.UPDATE: "update_all_permission",
            Action.DELETE: "delete_all_permission",
        }

        for perm in permissions:
            # Проверка права на доступ ко всем ресурсам
            all_permission_field = all_permission_map[action]
            if all_permission_field and getattr(perm, all_permission_field):
                return True

            # Проверка права на доступ к своим ресурсам
            own_permission_field = own_permission_map[action]
            if getattr(perm, own_permission_field):
                if action is Action.CREATE:
                    return True

                # Проверка, что ресурс принадлежит пользователю
                if resource_owner_id is not None and resource_owner_id == user_id:
                    return True

        return False
