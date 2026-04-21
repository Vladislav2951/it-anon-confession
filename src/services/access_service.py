from __future__ import annotations

from typing import TYPE_CHECKING, Optional

from domain.enums import Action
from domain.errors import ForbiddenError, UnauthorizedError
from domain.interfaces.database.uow import IDatabaseTransactionFactory


if TYPE_CHECKING:
    from pydantic import UUID7

    from domain.entities import Permission, User


class AccessService:
    """
    Access rights verification service.

    Implements authorization logic based on RBAC (Role-Based Access Control).
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
        1. Check user authentication and activity
        2. Get all user roles
        3. If no roles exist, access is denied
        4. Get access rules for roles and resources
        5. Check if at least one rule grants access
        6. If access is denied, an exception is thrown

        Args:
            user: Current user
            business_element_name: Business element name
            action: Action to perform
            resource_owner_id: Resource owner ID (for checking access to their resources)

        Raises:
            UnauthorizedError: User is not authenticated or inactive
            ForbiddenError: Insufficient rights (no roles or permissions)

        Example:
        await access_service.check_access(
            user=current_user,
            business_element_name="users",
            action=Action.UPDATE,
            resource_owner_id=user.id
        )
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
        """
        Checks whether an action based on rules is allowed.

        Validation logic:
            1. Rules are processed sequentially (OR logic)
            2. If there is a rule with access to all resources (read_all, update_all, delete_all), access is allowed
            3. If there is a rule with access to its own resources (read, update, delete):
                - For CREATE: access is always allowed
                - For other actions: resource_owner_id must match user_id

        Args:
            rules: List of access rules for user roles
            user_id: ID of the current user
            action: Action to perform
            resource_owner_id: ID of the resource owner (None for creation)

        Returns:
            bool: True if access is allowed, False otherwise
        """
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
