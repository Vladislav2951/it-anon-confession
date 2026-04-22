from unittest.mock import MagicMock

import pytest
from uuid_extensions import uuid7  # type: ignore[import-untyped]

from domain.entities import Permission, Role
from domain.entities.user import User
from domain.enums import SystemRole


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

    # async def test_admin_can_delete_user(self, auth_admin_client, mock_uow, test_admin):
    #     target_user_id = uuid7()
    #     mock_uow.role_repo.get_user_roles.return_value = [
    #         Role(id=uuid7(), name=SystemRole.admin.value, is_system=True)
    #     ]
    #     mock_uow.permission_repo.get_permissions_for_element.return_value = [
    #         Permission(
    #             id=uuid7(), business_element_id=uuid7(), delete_all_permission=True
    #         )
    #     ]
    #     # Админов в системе двое
    #     mock_uow.user_repo.get_all.return_value = [test_admin, MagicMock()]
    #     mock_uow.user_repo.get_one.return_value = MagicMock()

    #     response = await auth_admin_client.delete(f"/admin/users/{target_user_id}")
    #     assert response.status_code == 204

    @pytest.mark.asyncio
    async def test_admin_can_delete_user(self, auth_admin_client, mock_uow, test_admin):
        target_user_id = uuid7()
        # Создаем объект пользователя, которого будем "удалять"
        target_user_mock = MagicMock(spec=User)
        target_user_mock.id = target_user_id
        target_user_mock.is_active.return_value = True

        # Настраиваем get_one так, чтобы он различал админа и цель
        async def get_one_side_effect(uid, *args, **kwargs):
            if uid == test_admin.id:
                return test_admin  # Возвращаем админа для Middleware
            if uid == target_user_id:
                return target_user_mock  # Возвращаем цель для сервиса удаления
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

        # Чтобы проверка "последнего админа" прошла (их должно быть > 1)
        mock_uow.user_repo.get_all.return_value = [test_admin, MagicMock()]

        response = await auth_admin_client.delete(f"/admin/users/{target_user_id}")

        assert response.status_code == 204
