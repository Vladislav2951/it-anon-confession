import pytest
from uuid_extensions import uuid7  # type: ignore[import-untyped]

from domain.entities import BusinessElement, Permission, Role
from domain.enums import SystemRole


@pytest.mark.asyncio
class TestBusinessElementAdmin:
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

    async def test_get_all_business_elements_success(self, auth_admin_client, mock_uow):
        """Проверка успешного получения списка всех бизнес-элементов."""
        elements = [
            BusinessElement(id=uuid7(), name="users", description="User management"),
            BusinessElement(
                id=uuid7(), name="confessions", description="Confessions context"
            ),
        ]
        mock_uow.business_element_repo.get_all.return_value = elements

        response = await auth_admin_client.get("/admin/business-elements/")

        assert response.status_code == 200
        assert len(response.json()["data"]) == 2
        assert response.json()["data"][0]["name"] == "users"

    async def test_get_one_business_element_success(self, auth_admin_client, mock_uow):
        """Проверка получения одного элемента по ID."""
        element_id = uuid7()
        element = BusinessElement(id=element_id, name="admin", description="System admin")
        mock_uow.business_element_repo.get_one.return_value = element

        response = await auth_admin_client.get(f"/admin/business-elements/{element_id}")

        assert response.status_code == 200
        assert response.json()["data"]["id"] == str(element_id)
        assert response.json()["data"]["name"] == "admin"

    async def test_get_business_element_not_found(self, auth_admin_client, mock_uow):
        """Проверка 404 ошибки при запросе несуществующего элемента."""
        element_id = uuid7()
        mock_uow.business_element_repo.get_one.return_value = None

        response = await auth_admin_client.get(f"/admin/business-elements/{element_id}")

        assert response.status_code == 404


@pytest.mark.asyncio
class TestBusinessElementSecurity:
    async def test_regular_user_cannot_access_business_elements(
        self, auth_user_client, mock_uow, test_user
    ):
        """Обычный пользователь не должен иметь доступа к списку системных элементов."""
        mock_uow.user_repo.get_one.return_value = test_user
        mock_uow.role_repo.get_user_roles.return_value = [
            Role(id=uuid7(), name=SystemRole.user.value, is_system=True)
        ]
        # Пустой список прав для контекста admin
        mock_uow.permission_repo.get_permissions_for_element.return_value = []

        response = await auth_user_client.get("/admin/business-elements/")

        assert response.status_code == 403
