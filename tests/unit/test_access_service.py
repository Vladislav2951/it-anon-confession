import pytest
from uuid_extensions import uuid7  # type: ignore[import-untyped]

from domain.entities import Permission
from domain.enums import Action
from services.access_service import AccessService


@pytest.mark.asyncio
class TestAccessServiceUnit:
    async def test_is_allowed_logic(self, mock_uow_factory):
        service = AccessService(mock_uow_factory)
        # user_id = uuid7()

        # Разрешено чтение всего
        perm_read = Permission(
            id=uuid7(), business_element_id=uuid7(), read_permission=True
        )
        assert service._is_allowed(permissions=[perm_read], action=Action.READ) is True

        # Разрешено чтение только своего, запрашиваем чужое
        # perm_read_own = Permission(
        #     id=uuid7(), business_element_id=uuid7(), read_permission=True
        # )
        # assert (
        #     service._is_allowed(permissions=[perm_read_own], action=Action.READ) is False
        # )

        # Разрешено чтение только своего, запрашиваем свое
        # assert (
        #     service._is_allowed(permissions=[perm_read_own], action=Action.READ) is True
        # )

        # CREATE всегда True, если есть create_permission
        perm_create = Permission(
            id=uuid7(), business_element_id=uuid7(), create_permission=True
        )
        assert (
            service._is_allowed(permissions=[perm_create], action=Action.CREATE) is True
        )
