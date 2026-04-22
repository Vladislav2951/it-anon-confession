from httpx import AsyncClient
import pytest


@pytest.mark.asyncio
class TestAdminRestrictions:
    async def test_user_no_access_to_admin_routes(self, user_client: AsyncClient):
        response = await user_client.get("/admin/roles/")
        assert response.status_code == 403

    async def test_last_admin_cannot_delete_self(self, admin_client: AsyncClient):
        admin_id = "019ca1e5-c378-7000-8000-000000000201"
        response = await admin_client.delete(f"/admin/users/{admin_id}")

        assert response.status_code == 403
        assert "remove yourself" in response.json()["detail"]["message"]

    async def test_admin_can_delete_other_user(self, admin_client: AsyncClient):
        user_id = "019ca1e5-c378-7000-8000-000000000202"
        response = await admin_client.delete(f"/admin/users/{user_id}")
        assert response.status_code == 204
