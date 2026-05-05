from unittest.mock import MagicMock

import pytest
from uuid_extensions import uuid7  # type: ignore[import-untyped]

from domain.entities import Confession, Permission


@pytest.mark.asyncio
class TestConfessionsIntegration:
    async def test_user_can_read_all_confessions(self, auth_user_client, mock_uow):
        mock_uow.role_repo.get_user_roles.return_value = [MagicMock(name="user")]
        # Право read_permission на confessions
        mock_uow.permission_repo.get_permissions_for_element.return_value = [
            Permission(id=uuid7(), business_element_id=uuid7(), read_permission=True)
        ]
        mock_uow.confession_repo.get_all.return_value = (
            [
                Confession(
                    id=uuid7(),
                    title="Test",
                    body="Secret",
                    authored_by="anon",
                    user_id=uuid7(),
                    created_at="2023-01-01T00:00:00Z",
                )
            ],
            1,
        )

        response = await auth_user_client.get("/confessions/")
        assert response.status_code == 200
        assert len(response.json()["data"]) == 1

    async def test_user_cannot_update_confession(self, auth_user_client, mock_uow):
        conf_id = uuid7()
        mock_uow.role_repo.get_user_roles.return_value = [MagicMock(name="user")]
        # У юзера нет update_permission в моке
        mock_uow.permission_repo.get_permissions_for_element.return_value = [
            Permission(id=uuid7(), business_element_id=uuid7(), read_permission=True)
        ]

        response = await auth_user_client.patch(
            f"/confessions/{conf_id}", json={"title": "new"}
        )
        assert response.status_code == 403
