from httpx import AsyncClient
import pytest


@pytest.mark.asyncio
class TestAuth:
    async def test_login_success(self, client: AsyncClient):
        response = await client.post(
            "/auth/login", json={"email": "admin@example.com", "password": "admin123"}
        )
        assert response.status_code == 200
        assert "session_id" in response.cookies

    async def test_login_wrong_password(self, client: AsyncClient):
        response = await client.post(
            "/auth/login", json={"email": "admin@example.com", "password": "wrong"}
        )
        assert response.status_code == 401
        assert response.json()["detail"] == "Incorrect email or password"

    async def test_register_duplicate_email(self, client: AsyncClient):
        response = await client.post(
            "/auth/register",
            json={
                "email": "admin@example.com",
                "password": "newpassword123",
                "password_repeat": "newpassword123",
                "nickname": "newbie",
                "bio": "hello",
            },
        )
        assert response.status_code == 409
        assert response.json()["detail"]["code"] == "CONFLICT"

    async def test_logout(self, user_client: AsyncClient):
        response = await user_client.post("/auth/logout")
        assert response.status_code == 200
        # Cookie should be cleared (max-age=0 or deleted)
        assert response.cookies.get("session_id") is None
