from unittest.mock import AsyncMock, MagicMock
import uuid

import pytest

from domain.entities import Permission, User
from domain.enums import Action
from domain.errors import ForbiddenError
from services.access_service import AccessService


class TestAccessServiceUnit:
    @pytest.mark.asyncio
    async def test_check_access_system_element(self):
        factory = MagicMock()
        service = AccessService(factory)
        await service.check_access(None, "__system__", Action.READ)
        factory.assert_not_called()

    def test_is_allowed_logic(self):
        service = AccessService(MagicMock())
        user_id = uuid.UUID("019ca1e5-c378-7000-8000-000000000202")
        someone_else = uuid.UUID("019ca1e5-c378-7000-8000-000008800200")

        # Есть право read_all
        perm_all = MagicMock(spec=Permission)
        perm_all.read_all_permission = True
        perm_all.read_permission = False

        assert (
            service._is_allowed(
                permissions=[perm_all],
                user_id=user_id,
                action=Action.READ,
                resource_owner_id=someone_else,
            )
            is True
        )

        # Есть только право read (свое), а ресурс чужой
        perm_own = MagicMock(spec=Permission)
        perm_own.read_all_permission = False
        perm_own.read_permission = True

        assert (
            service._is_allowed(
                permissions=[perm_own],
                user_id=user_id,
                action=Action.READ,
                resource_owner_id=someone_else,
            )
            is False
        )

        # Ресурс свой
        assert (
            service._is_allowed(
                permissions=[perm_own],
                user_id=user_id,
                action=Action.READ,
                resource_owner_id=user_id,
            )
            is True
        )
