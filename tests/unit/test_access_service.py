from unittest.mock import MagicMock
import uuid

import pytest
from uuid_extensions import uuid7  # type: ignore[import-untyped]

from domain.entities import Permission
from domain.enums import Action
from services.access_service import AccessService


@pytest.mark.asyncio
class TestAccessServiceUnit:
    async def test_system_bypass(self, mock_uow_factory):
        service = AccessService(mock_uow_factory)
        # Элемент __system__ не должен даже обращаться к БД
        await service.check_access(None, "__system__", Action.READ)
        mock_uow_factory.assert_not_called()

    async def test_is_allowed_logic(self, mock_uow_factory):
        service = AccessService(mock_uow_factory)
        user_id = uuid7()

        # Разрешено чтение всего
        perm_read_all = Permission(
            id=uuid7(), business_element_id=uuid7(), read_all_permission=True
        )
        assert (
            service._is_allowed(
                permissions=[perm_read_all],
                user_id=user_id,
                action=Action.READ,
                resource_owner_id=uuid7(),
            )
            is True
        )

        # Разрешено чтение только своего, запрашиваем чужое
        perm_read_own = Permission(
            id=uuid7(), business_element_id=uuid7(), read_permission=True
        )
        assert (
            service._is_allowed(
                permissions=[perm_read_own],
                user_id=user_id,
                action=Action.READ,
                resource_owner_id=uuid7(),
            )
            is False
        )

        # Разрешено чтение своего, запрашиваем свое
        assert (
            service._is_allowed(
                permissions=[perm_read_own],
                user_id=user_id,
                action=Action.READ,
                resource_owner_id=user_id,
            )
            is True
        )

        # CREATE всегда True, если есть create_permission
        perm_create = Permission(
            id=uuid7(), business_element_id=uuid7(), create_permission=True
        )
        assert (
            service._is_allowed(
                permissions=[perm_create],
                user_id=user_id,
                action=Action.CREATE,
                resource_owner_id=None,
            )
            is True
        )
