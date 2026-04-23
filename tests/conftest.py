from typing import AsyncGenerator
from unittest.mock import AsyncMock, MagicMock

from httpx import ASGITransport, AsyncClient
import pytest
from uuid_extensions import uuid7  # type: ignore[import-untyped]

from core import dependencies
from domain.entities import Session, User
from main import app


@pytest.fixture
def mock_uow():
    uow = MagicMock()
    uow.user_repo = AsyncMock()
    uow.session_repo = AsyncMock()
    uow.role_repo = AsyncMock()
    uow.permission_repo = AsyncMock()
    uow.confession_repo = AsyncMock()
    uow.business_element_repo = AsyncMock()

    # Настройка контекстного менеджера (async with)
    uow.__aenter__.return_value = uow
    uow.__aexit__.return_value = None
    return uow


@pytest.fixture
def mock_uow_factory(mock_uow):
    factory = MagicMock()
    factory.return_value = mock_uow
    return factory


@pytest.fixture
async def client(mock_uow_factory) -> AsyncGenerator[AsyncClient, None]:
    """Клиент с переопределенными сервисами на базе моков."""
    from services import (
        AccessService,
        AuthService,
        BusinessElementService,
        ConfessionService,
        PermissionService,
        RoleService,
        SessionService,
        UserService,
    )

    # Инициализация сервисов с мок-фабрикой
    t_access = AccessService(mock_uow_factory)
    t_auth = AuthService(mock_uow_factory)
    t_session = SessionService(mock_uow_factory)
    t_user = UserService(mock_uow_factory, t_access)
    t_role = RoleService(mock_uow_factory, t_access)
    t_conf = ConfessionService(mock_uow_factory, t_access)
    t_be = BusinessElementService(mock_uow_factory, t_access)
    t_permission = PermissionService(mock_uow_factory, t_access)

    # Зависимости в FastAPI
    app.dependency_overrides[dependencies.auth_srv] = lambda: t_auth
    app.dependency_overrides[dependencies.session_srv] = lambda: t_session
    app.dependency_overrides[dependencies.user_srv] = lambda: t_user
    app.dependency_overrides[dependencies.role_srv] = lambda: t_role
    app.dependency_overrides[dependencies.access_srv] = lambda: t_access
    app.dependency_overrides[dependencies.confession_srv] = lambda: t_conf
    app.dependency_overrides[dependencies.business_element_srv] = lambda: t_be
    app.dependency_overrides[dependencies.permission_srv] = lambda: t_permission

    async with AsyncClient(
        transport=ASGITransport(app=app), base_url="http://test"
    ) as ac:
        yield ac
    app.dependency_overrides.clear()


@pytest.fixture
def test_user():
    return User(
        id=uuid7(),
        email="user@test.com",
        password_hash="hashed",
        nickname="tester",
        bio="I am a tester",
    )


@pytest.fixture
def test_admin():
    return User(
        id=uuid7(),
        email="admin@test.com",
        password_hash="hashed",
        nickname="admin",
        bio="I am admin",
    )


@pytest.fixture
async def auth_user_client(client, mock_uow, test_user):
    """Клиент, авторизованный как обычный пользователь."""
    session = MagicMock(spec=Session)
    session.user_id = test_user.id
    session.is_expired.return_value = False

    mock_uow.session_repo.get_one.return_value = session
    mock_uow.user_repo.get_one.return_value = test_user

    client.cookies.set("session_id", "fake-token")
    return client


@pytest.fixture
async def auth_admin_client(client, mock_uow, test_admin):
    """Клиент, авторизованный как админ."""
    session = MagicMock(spec=Session)
    session.user_id = test_admin.id
    session.is_expired.return_value = False

    mock_uow.session_repo.get_one.return_value = session
    mock_uow.user_repo.get_one.return_value = test_admin

    client.cookies.set("session_id", "fake-admin-token")
    return client
