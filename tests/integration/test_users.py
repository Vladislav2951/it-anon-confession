from unittest.mock import MagicMock

import pytest
from uuid_extensions import uuid7  # type: ignore[import-untyped]

from domain.entities import Permission


@pytest.mark.asyncio
class TestUserPermissionsIntegration:
    async def test_user_get_own_profile(self, auth_user_client, mock_uow, test_user):
        mock_uow.role_repo.get_user_roles.return_value = [
            MagicMock(id=uuid7(), name="user")
        ]
        mock_uow.permission_repo.get_permissions_for_element.return_value = [
            Permission(id=uuid7(), business_element_id=uuid7(), read_permission=True)
        ]
        mock_uow.user_repo.get_one.return_value = test_user

        response = await auth_user_client.get(f"/users/{test_user.id}")
        assert response.status_code == 200
        assert response.json()["data"]["email"] == test_user.email

    async def test_user_cannot_get_others_profile(self, auth_user_client, mock_uow):
        other_id = uuid7()
        mock_uow.role_repo.get_user_roles.return_value = [MagicMock(name="user")]
        mock_uow.permission_repo.get_permissions_for_element.return_value = [
            Permission(id=uuid7(), business_element_id=uuid7(), read_own_permission=True)
        ]

        response = await auth_user_client.get(f"/users/{other_id}")
        assert response.status_code == 403
        assert "Access denied" in response.json()["detail"]["message"]

    async def test_admin_can_list_all_users(
        self, auth_admin_client, mock_uow, test_admin
    ):
        mock_uow.role_repo.get_user_roles.return_value = [MagicMock(name="admin")]
        mock_uow.permission_repo.get_permissions_for_element.return_value = [
            Permission(id=uuid7(), business_element_id=uuid7(), read_permission=True)
        ]
        mock_uow.user_repo.count.return_value = 1
        mock_uow.user_repo.get_all.return_value = [test_admin]

        response = await auth_admin_client.get("/admin/users/")
        assert response.status_code == 200
        assert len(response.json()["data"]) == 1
