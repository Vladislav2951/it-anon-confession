from unittest.mock import MagicMock

import pytest
from uuid_extensions import uuid7  # type: ignore[import-untyped]

from domain.entities import Permission, Role
from domain.enums import SystemRole


@pytest.mark.asyncio
class TestRolePermissionManagement:
    @pytest.fixture(autouse=True)
    def setup_admin_access(self, mock_uow, test_admin):
        """Настройка админа для каждого теста в классе."""
        mock_uow.user_repo.get_one.return_value = test_admin
        mock_uow.role_repo.get_user_roles.return_value = [
            Role(id=uuid7(), name=SystemRole.admin.value, is_system=True)
        ]

        permission = Permission(
            id=uuid7(),
            business_element_id=uuid7(),
            read_all_permission=True,
            update_all_permission=True,
            delete_all_permission=True,
            create_permission=True,
        )
        mock_uow.permission_repo.get_permissions_for_element.return_value = [permission]

    async def test_assign_permission_to_role_success(self, auth_admin_client, mock_uow):
        role_id = uuid7()
        perm_id = uuid7()

        # Настройка моков для middleware и проверки существования
        mock_uow.permission_repo.get_one.return_value = MagicMock(spec=Permission)

        # Права доступа админа
        mock_uow.role_repo.get_user_roles.return_value = [Role(id=uuid7(), name="admin")]

        response = await auth_admin_client.post(
            f"/admin/roles/{role_id}/assign-permission/{perm_id}"
        )

        assert response.status_code == 204
        mock_uow.role_repo.assign_permission.assert_called_once_with(role_id, perm_id)

    async def test_assign_permission_conflict(
        self, auth_admin_client, mock_uow, test_admin
    ):
        role_id = uuid7()
        perm_id = uuid7()

        mock_uow.user_repo.get_one.return_value = test_admin

        # Уже назначено
        from domain.errors import ConflictError

        mock_uow.role_repo.assign_permission.side_effect = ConflictError(
            "Already assigned"
        )

        # Нарушение Unique Constraint)
        mock_uow.role_repo.assign_permission.side_effect = ConflictError(
            "Permission already assigned to this role"
        )

        response = await auth_admin_client.post(
            f"/admin/roles/{role_id}/assign-permission/{perm_id}"
        )

        assert response.status_code == 409
        assert response.json()["detail"]["code"] == "CONFLICT"

    async def test_revoke_permission_from_role_success(
        self, auth_admin_client, mock_uow, test_admin
    ):
        role_id = uuid7()
        perm_id = uuid7()

        mock_uow.user_repo.get_one.return_value = test_admin

        response = await auth_admin_client.post(
            f"/admin/roles/{role_id}/revoke-permission/{perm_id}"
        )

        assert response.status_code == 204
        mock_uow.role_repo.revoke_permission.assert_called_once_with(role_id, perm_id)
