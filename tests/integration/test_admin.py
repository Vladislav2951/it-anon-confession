from unittest.mock import MagicMock

import pytest
from uuid_extensions import uuid7  # type: ignore[import-untyped]

from domain.entities import Permission, Role
from domain.entities.user import User
from domain.enums import SystemRole
from domain.errors import ConflictError


@pytest.mark.asyncio
class TestAdminProtection:
    async def test_last_admin_cannot_delete_himself(
        self, auth_admin_client, mock_uow, test_admin
    ):
        mock_uow.role_repo.get_user_roles.return_value = [
            Role(id=uuid7(), name=SystemRole.admin.value, is_system=True)
        ]
        mock_uow.permission_repo.get_permissions_for_element.return_value = [
            Permission(
                id=uuid7(), business_element_id=uuid7(), delete_all_permission=True
            )
        ]
        # В системе только один админ (он сам)
        mock_uow.user_repo.get_all.return_value = [test_admin]

        response = await auth_admin_client.delete(f"/admin/users/{test_admin.id}")

        assert response.status_code == 403
        assert (
            "Are you trying to remove yourself?" in response.json()["detail"]["message"]
        )

    @pytest.mark.asyncio
    async def test_admin_can_delete_user(self, auth_admin_client, mock_uow, test_admin):
        target_user_id = uuid7()
        # Объект пользователя, которого будем удалять
        target_user_mock = MagicMock(spec=User)
        target_user_mock.id = target_user_id
        target_user_mock.is_active.return_value = True

        # Настройка get_one так, чтобы он различал админа и цель
        async def get_one_side_effect(uid, *args, **kwargs):
            if uid == test_admin.id:
                return test_admin  # Админ для Middleware
            if uid == target_user_id:
                return target_user_mock  # Админ для сервиса удаления
            return None

        mock_uow.user_repo.get_one.side_effect = get_one_side_effect

        # Настройка прав для проверки внутри soft_delete
        mock_uow.role_repo.get_user_roles.return_value = [
            Role(id=uuid7(), name=SystemRole.admin.value, is_system=True)
        ]
        mock_uow.permission_repo.get_permissions_for_element.return_value = [
            Permission(
                id=uuid7(), business_element_id=uuid7(), delete_all_permission=True
            )
        ]

        # Чтобы проверка последнего админа прошла (их должно быть > 1)
        mock_uow.user_repo.get_all.return_value = [test_admin, MagicMock()]

        response = await auth_admin_client.delete(f"/admin/users/{target_user_id}")

        assert response.status_code == 204

    async def test_revoke_admin_role_fails_if_last_admin(
        self, auth_admin_client, mock_uow, test_admin
    ):
        """Нельзя снять роль админа, если он последний в системе."""
        role_id = uuid7()

        mock_uow.user_repo.get_one.return_value = test_admin
        mock_uow.role_repo.get_user_roles.return_value = [
            Role(id=uuid7(), name=SystemRole.admin.value, is_system=True)
        ]
        mock_uow.permission_repo.get_permissions_for_element.return_value = [
            Permission(
                id=uuid7(), business_element_id=uuid7(), update_all_permission=True
            )
        ]

        mock_uow.role_repo.get_one.return_value = Role(
            id=role_id, name=SystemRole.admin.value, is_system=True
        )

        # Имитация в системе только одного админ
        mock_uow.user_repo.get_all.return_value = [test_admin]

        response = await auth_admin_client.post(
            f"/admin/users/{test_admin.id}/revoke-role/{role_id}"
        )

        assert response.status_code == 403
        assert "last administrator role" in response.json()["detail"]["message"]
        # Убеждаемся, что метод удаления в репозитории не был вызван
        mock_uow.user_repo.revoke_role.assert_not_called()

    async def test_revoke_admin_role_success_if_not_last(
        self, auth_admin_client, mock_uow, test_admin
    ):
        """Проверка: снять роль админа можно, если в системе есть кто-то еще."""
        role_id = uuid7()
        target_user_id = uuid7()

        mock_uow.user_repo.get_one.return_value = test_admin
        mock_uow.role_repo.get_user_roles.return_value = [
            Role(id=uuid7(), name=SystemRole.admin.value, is_system=True)
        ]
        mock_uow.permission_repo.get_permissions_for_element.return_value = [
            Permission(
                id=uuid7(), business_element_id=uuid7(), update_all_permission=True
            )
        ]

        # Мокаем двух админов
        another_admin = MagicMock(spec=User, id=uuid7())
        mock_uow.user_repo.get_all.return_value = [test_admin, another_admin]

        # Настройка get_one для Middleware и логики
        mock_uow.user_repo.get_one.side_effect = lambda uid: (
            test_admin if uid == test_admin.id else MagicMock(id=target_user_id)
        )

        response = await auth_admin_client.post(
            f"/admin/users/{target_user_id}/revoke-role/{role_id}"
        )

        assert response.status_code == 204
        mock_uow.user_repo.revoke_role.assert_called_once_with(target_user_id, role_id)


@pytest.mark.asyncio
class TestAdminUserRoleManagement:
    @pytest.fixture(autouse=True)
    def setup_admin_god_mode(self, mock_uow, test_admin):
        """Настройка полного доступа для админа в каждом тесте."""
        mock_uow.user_repo.get_one.return_value = test_admin
        mock_uow.role_repo.get_user_roles.return_value = [
            Role(id=uuid7(), name=SystemRole.admin.value, is_system=True)
        ]
        god_permission = Permission(
            id=uuid7(),
            business_element_id=uuid7(),
            update_all_permission=True,
            read_all_permission=True,
        )
        mock_uow.permission_repo.get_permissions_for_element.return_value = [
            god_permission
        ]

    async def test_assign_role_to_user_success(
        self, auth_admin_client, mock_uow, test_admin
    ):
        target_user_id = uuid7()
        role_id = uuid7()

        # Проверка существования
        def get_one_side_effect(uid, *args, **kwargs):
            if uid == test_admin.id:
                return test_admin
            return MagicMock()  # Для целевого юзера

        mock_uow.user_repo.get_one.side_effect = get_one_side_effect
        mock_uow.role_repo.get_one.return_value = MagicMock(spec=Role)

        response = await auth_admin_client.post(
            f"/admin/users/{target_user_id}/assign-role/{role_id}"
        )

        assert response.status_code == 204
        mock_uow.user_repo.assign_role.assert_called_once_with(target_user_id, role_id)

    async def test_assign_role_conflict(self, auth_admin_client, mock_uow, test_admin):
        target_user_id = uuid7()
        role_id = uuid7()

        mock_uow.user_repo.get_one.side_effect = lambda uid: (
            test_admin if uid == test_admin.id else MagicMock()
        )
        mock_uow.role_repo.get_one.return_value = MagicMock()

        mock_uow.user_repo.assign_role.side_effect = ConflictError()

        response = await auth_admin_client.post(
            f"/admin/users/{target_user_id}/assign-role/{role_id}"
        )

        assert response.status_code == 409

    async def test_revoke_role_success(self, auth_admin_client, mock_uow, test_admin):
        target_user_id = uuid7()
        role_id = uuid7()

        mock_uow.user_repo.get_one.side_effect = lambda uid: (
            test_admin if uid == test_admin.id else MagicMock()
        )
        mock_uow.role_repo.get_one.return_value = MagicMock()

        response = await auth_admin_client.post(
            f"/admin/users/{target_user_id}/revoke-role/{role_id}"
        )

        assert response.status_code == 204
        mock_uow.user_repo.revoke_role.assert_called_once_with(target_user_id, role_id)

    async def test_assign_role_user_not_found(
        self, auth_admin_client, mock_uow, test_admin
    ):
        target_user_id = uuid7()
        role_id = uuid7()

        # User не существует
        mock_uow.user_repo.get_one.side_effect = lambda uid: (
            test_admin if uid == test_admin.id else None
        )

        response = await auth_admin_client.post(
            f"/admin/users/{target_user_id}/assign-role/{role_id}"
        )

        assert response.status_code == 404
