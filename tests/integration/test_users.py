from httpx import AsyncClient
import pytest


@pytest.mark.asyncio
class TestUserAccess:
    async def test_user_can_read_self(self, user_client: AsyncClient):
        # ID пользователя python_fan из seed
        user_id = "019ca1e5-c378-7000-8000-000000000202"
        response = await user_client.get(f"/users/{user_id}")
        assert response.status_code == 200
        assert response.json()["data"]["email"] == "python_fan@example.com"

    async def test_user_cannot_read_other(self, user_client: AsyncClient):
        # ID админа
        admin_id = "019ca1e5-c378-7000-8000-000000000201"
        response = await user_client.get(f"/users/{admin_id}")
        assert response.status_code == 403
        assert "Access denied" in response.json()["detail"]["message"]

    async def test_admin_can_read_anyone(self, admin_client: AsyncClient):
        user_id = "019ca1e5-c378-7000-8000-000000000202"
        response = await admin_client.get(f"/users/{user_id}")
        assert response.status_code == 200
        assert response.json()["data"]["nickname"] == "python_fan"
