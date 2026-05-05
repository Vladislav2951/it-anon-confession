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
            read_permission=True,
            update_permission=True,
            delete_permission=True,
            create_permission=True,
        )
        mock_uow.permission_repo.get_permissions_for_element.return_value = [permission]

    async def test_assign_permission_to_role_success(self, auth_admin_client, mock_uow):
        role_id = uuid7()
        perm_id = uuid7()

        role = Role(id=uuid7(), name="user")
        mock_uow.role_repo.get_one.return_value = role
        mock_uow.role_repo.get_user_roles.return_value = [role]
        mock_uow.permission_repo.get_one.return_value = MagicMock(spec=Permission)

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

        from domain.errors import ConflictError

        mock_uow.role_repo.assign_permission.side_effect = ConflictError(
            "Already assigned"
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
        role = Role(id=uuid7(), name="user")
        mock_uow.role_repo.get_one.return_value = role

        response = await auth_admin_client.post(
            f"/admin/roles/{role_id}/revoke-permission/{perm_id}"
        )

        assert response.status_code == 204
        mock_uow.role_repo.revoke_permission.assert_called_once_with(role_id, perm_id)
