import pytest
from uuid_extensions import uuid7  # type: ignore[import-untyped]

from domain.entities import Permission, Role
from domain.enums import SystemRole


@pytest.mark.asyncio
class TestPermissionAdmin:
    """Группа тестов для управления правами (Permissions) в админ-панели."""

    @pytest.fixture(autouse=True)
    def setup_admin_access(self, mock_uow, test_admin):
        """Настройка админа для каждого теста в классе."""
        mock_uow.user_repo.get_one.return_value = test_admin
        mock_uow.role_repo.get_user_roles.return_value = [
            Role(id=uuid7(), name=SystemRole.admin.value, is_system=True)
        ]

        permission = Permission(
            id=uuid7(), business_element_id=uuid7(), read_all_permission=True
        )
        mock_uow.permission_repo.get_permissions_for_element.return_value = [permission]

    async def test_get_all_permissions_success(self, auth_admin_client, mock_uow):
        """Проверка получения списка всех существующих разрешений."""
        permissions_list = [
            Permission(
                id=uuid7(),
                business_element_id=uuid7(),
                read_all_permission=True,
                description="All Read",
            ),
            Permission(
                id=uuid7(),
                business_element_id=uuid7(),
                create_permission=True,
                description="Create Own",
            ),
        ]
        mock_uow.permission_repo.get_all.return_value = permissions_list

        response = await auth_admin_client.get("/admin/permissions/")

        assert response.status_code == 200
        assert len(response.json()["data"]) == 2
        assert response.json()["data"][0]["description"] == "All Read"

    async def test_get_one_permission_success(self, auth_admin_client, mock_uow):
        """Проверка получения конкретного разрешения по ID."""
        perm_id = uuid7()
        permission = Permission(
            id=perm_id,
            business_element_id=uuid7(),
            read_permission=True,
            description="Specific Perm",
        )
        mock_uow.permission_repo.get_one.return_value = permission

        response = await auth_admin_client.get(f"/admin/permissions/{perm_id}")

        assert response.status_code == 200
        assert response.json()["data"]["id"] == str(perm_id)
        assert response.json()["data"]["description"] == "Specific Perm"

    async def test_get_permission_not_found(self, auth_admin_client, mock_uow):
        """Проверка возврата 404, если разрешение не найдено."""
        perm_id = uuid7()
        mock_uow.permission_repo.get_one.return_value = None

        response = await auth_admin_client.get(f"/admin/permissions/{perm_id}")

        assert response.status_code == 404


@pytest.mark.asyncio
class TestPermissionSecurity:
    """Группа тестов для проверки ограничений доступа к permissions."""

    async def test_user_cannot_access_permissions_list(
        self, auth_user_client, mock_uow, test_user
    ):
        """Обычный пользователь не должен видеть список системных разрешений."""
        mock_uow.user_repo.get_one.return_value = test_user
        mock_uow.role_repo.get_user_roles.return_value = [
            Role(id=uuid7(), name=SystemRole.user.value, is_system=True)
        ]
        # У юзера нет прав на элемент 'admin'
        mock_uow.permission_repo.get_permissions_for_element.return_value = []

        response = await auth_user_client.get("/admin/permissions/")

        assert response.status_code == 403
