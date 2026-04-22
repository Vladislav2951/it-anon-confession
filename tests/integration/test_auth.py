from unittest.mock import MagicMock

import pytest
from uuid_extensions import uuid7  # type: ignore[import-untyped]


@pytest.mark.asyncio
class TestAuthIntegration:
    async def test_register_success(self, client, mock_uow):
        # Пользователь не зарегистрирован
        mock_uow.user_repo.get_one_by_email.return_value = None
        # Получение роли user
        mock_uow.role_repo.get_one_by_name.return_value = MagicMock(id=uuid7())

        response = await client.post(
            "/auth/register",
            json={
                "email": "new@test.com",
                "password": "password123",
                "password_repeat": "password123",
                "nickname": "newbie",
                "bio": "hello",
            },
        )
        assert response.status_code == 201
        assert response.json()["message"] == "User has been registered"

    async def test_register_password_mismatch(self, client):
        response = await client.post(
            "/auth/register",
            json={
                "email": "new@test.com",
                "password": "password123",
                "password_repeat": "different",
                "nickname": "newbie",
                "bio": "hi",
            },
        )
        assert response.status_code == 422  # Pydantic validation error

    async def test_login_incorrect_credentials(self, client, mock_uow):
        mock_uow.user_repo.get_one_by_email.return_value = None

        response = await client.post(
            "/auth/login", json={"email": "wrong@test.com", "password": "any"}
        )
        assert response.status_code == 401
        assert "Incorrect email or password" in response.text
