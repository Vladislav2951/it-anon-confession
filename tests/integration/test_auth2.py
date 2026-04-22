from fastapi import status
import pytest


@pytest.mark.asyncio
class TestAuthentication:
    async def test_register_success(self, client, db_session):
        response = await client.post(
            "/auth/register",
            json={
                "email": "new@example.com",
                "password": "password123",
                "password_repeat": "password123",
                "nickname": "newuser",
                "bio": "Hello",
            },
        )
        assert response.status_code == status.HTTP_201_CREATED
        assert response.json()["message"] == "User has been registered"

    async def test_register_password_mismatch(self, client):
        response = await client.post(
            "/auth/register",
            json={
                "email": "fail@example.com",
                "password": "password123",
                "password_repeat": "different",
                "nickname": "fail",
                "bio": "",
            },
        )
        assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY

    async def test_login_wrong_credentials(self, client, create_user):
        await create_user("test@test.com", "correct_pass", "tester")
        response = await client.post(
            "/auth/login", json={"email": "test@test.com", "password": "wrong_password"}
        )
        assert response.status_code == status.HTTP_401_UNAUTHORIZED
        assert "Incorrect email or password" in response.json()["detail"]

    async def test_logout(self, auth_client, create_user):
        user = await create_user("out@test.com", "pass123", "out")
        authenticated_client = await auth_client(user["email"], user["password"])

        response = await authenticated_client.post("/auth/logout")
        assert response.status_code == status.HTTP_200_OK
        assert "session_id" not in authenticated_client.cookies
