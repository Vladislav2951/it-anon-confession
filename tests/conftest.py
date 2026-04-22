import asyncio
from typing import AsyncGenerator
import uuid

from httpx import ASGITransport, AsyncClient
import pytest
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine
from sqlalchemy.pool import StaticPool

from core import dependencies
from infrastructure.postgres.models import (
    Base,
    BusinessElementModel,
    PermissionModel,
    RoleModel,
    UserModel,
    role_permissions,
    user_roles,
)
from infrastructure.postgres.uow import TransactionFactory, TransactionUoW
from main import app
from services import *


# Константы из миграции fa6c26a70384
ADMIN_ID = uuid.UUID("019ca1e5-c378-7000-8000-000000000201")
USER_1_ID = uuid.UUID("019ca1e5-c378-7000-8000-000000000202")
ROLE_USER_ID = uuid.UUID("019ca1e5-c378-7000-8000-000000000102")
ROLE_ADMIN_ID = uuid.UUID("019ca1e5-c378-7000-8000-000000000101")

# ADMIN_DB_URL = "postgresql+asyncpg://postgres:postgres@localhost:5432/postgres"
# TEST_DB_NAME = "test_postgres"
# TEST_DATABASE_URL = (
#     f"postgresql+asyncpg://postgres:postgres@localhost:5432/{TEST_DB_NAME}"
# )

# Настройка SQLite в памяти
# StaticPool важен: он держит одно соединение открытым всю сессию
TEST_DATABASE_URL = "sqlite+aiosqlite:///:memory:"
test_engine = create_async_engine(
    TEST_DATABASE_URL, connect_args={"check_same_thread": False}, poolclass=StaticPool
)
test_session_maker = async_sessionmaker(test_engine, expire_on_commit=False)

# test_engine = create_async_engine(TEST_DATABASE_URL)
# test_session_maker = async_sessionmaker(test_engine, expire_on_commit=False)


@pytest.fixture(scope="session")
def event_loop():
    """Создает экземпляр стандартного цикла событий для всей тестовой сессии."""
    loop = asyncio.get_event_loop_policy().new_event_loop()
    yield loop
    loop.close()


# Класс для перехвата UoW
class TestTransactionFactory(TransactionFactory):
    def __call__(self):
        return TransactionUoW(test_session_maker)


# async def create_db_if_not_exists():
#     """Создает базу в режиме AUTOCOMMIT"""
#     admin_engine = create_async_engine(TEST_DATABASE_URL, isolation_level="AUTOCOMMIT")
#     async with admin_engine.connect() as conn:
#         res = await conn.execute(
#             text(f"SELECT 1 FROM pg_database WHERE datname = '{TEST_DB_NAME}'")
#         )
#         if not res.scalar():
#             await conn.execute(text(f"CREATE DATABASE {TEST_DB_NAME}"))
#     await admin_engine.dispose()


@pytest.fixture(scope="session", autouse=True)
async def setup_db():
    """Создает структуру БД один раз на всю сессию."""
    async with test_engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    async with test_session_maker() as session:
        await seed_test_data(session)

    yield

    async with test_engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)
    await test_engine.dispose()


@pytest.fixture
async def client() -> AsyncGenerator[AsyncClient, None]:
    """Перехват всех зависимостей сервисов"""
    test_uow_factory = TestTransactionFactory()

    # Создаем тестовые экземпляры сервисов с тестовым UoW
    t_access = AccessService(test_uow_factory)
    t_auth = AuthService(test_uow_factory)
    t_session = SessionService(test_uow_factory)
    t_user = UserService(test_uow_factory, t_access)
    t_role = RoleService(test_uow_factory, t_access)
    t_conf = ConfessionService(test_uow_factory, t_access)

    # Подменяем функции из core.dependencies
    app.dependency_overrides[dependencies.auth_srv] = lambda: t_auth
    app.dependency_overrides[dependencies.session_srv] = lambda: t_session
    app.dependency_overrides[dependencies.user_srv] = lambda: t_user
    app.dependency_overrides[dependencies.role_srv] = lambda: t_role
    app.dependency_overrides[dependencies.access_srv] = lambda: t_access
    app.dependency_overrides[dependencies.confession_srv] = lambda: t_conf

    async with AsyncClient(
        transport=ASGITransport(app=app), base_url="http://test"
    ) as ac:
        yield ac
    app.dependency_overrides.clear()


# @pytest.fixture
# async def client() -> AsyncGenerator[AsyncClient, None]:
#     app.dependency_overrides[_database_uow_factory] = lambda: TestUoW()
#     async with AsyncClient(
#         transport=ASGITransport(app=app), base_url="http://test"
#     ) as ac:
#         yield ac


@pytest.fixture
async def admin_client(client: AsyncClient):
    await client.post(
        "/auth/login", json={"email": "admin@example.com", "password": "admin123"}
    )
    return client


@pytest.fixture
async def user_client(client: AsyncClient):
    await client.post(
        "/auth/login", json={"email": "user@example.com", "password": "admin123"}
    )
    return client


async def seed_test_data(session: AsyncSession):
    # 1. Business Elements
    be_users = BusinessElementModel(
        id=uuid.UUID("019ca1e5-c378-7000-8000-000000000001"), name="users"
    )
    be_admin = BusinessElementModel(
        id=uuid.UUID("019ca1e5-c378-7000-8000-000000000002"), name="admin"
    )
    be_conf = BusinessElementModel(
        id=uuid.UUID("019ca1e5-c378-7000-8000-000000000003"), name="confessions"
    )
    session.add_all([be_users, be_admin, be_conf])

    # 2. Roles
    role_admin = RoleModel(id=ROLE_ADMIN_ID, name="admin", is_system=True)
    role_user = RoleModel(id=ROLE_USER_ID, name="user", is_system=True)
    session.add_all([role_admin, role_user])

    # 3. Users (password: admin123)
    pwd_hash = "$2b$12$ANfB7EKjY/hncfbXpRjpIOt9EO8DFCpv0b9OXkYnaVBNDjoAZ933."
    admin_user = UserModel(
        id=ADMIN_ID, email="admin@example.com", password_hash=pwd_hash, nickname="admin"
    )
    normal_user = UserModel(
        id=USER_1_ID,
        email="user@example.com",
        password_hash=pwd_hash,
        nickname="python_fan",
    )
    session.add_all([admin_user, normal_user])

    await session.flush()

    # 4. Permissions (Simplified to match migration)
    p1 = PermissionModel(
        id=uuid.UUID("019ca1e5-c378-7000-8000-000000000301"),
        business_element_id=be_users.id,
        read_permission=True,
        read_all_permission=True,
        create_permission=True,
        update_permission=True,
        update_all_permission=True,
        delete_permission=True,
        delete_all_permission=True,
    )
    p2 = PermissionModel(
        id=uuid.UUID("019ca1e5-c378-7000-8000-000000000302"),
        business_element_id=be_admin.id,
        read_permission=True,
        read_all_permission=True,
        create_permission=True,
        update_permission=True,
        update_all_permission=True,
        delete_permission=True,
        delete_all_permission=True,
    )
    p3 = PermissionModel(
        id=uuid.UUID("019ca1e5-c378-7000-8000-000000000304"),
        business_element_id=be_users.id,
        read_permission=True,
        update_permission=True,
    )  # User own profile
    p4 = PermissionModel(
        id=uuid.UUID("019ca1e5-c378-7000-8000-000000000305"),
        business_element_id=be_conf.id,
        read_permission=True,
        read_all_permission=True,
        create_permission=True,
    )
    session.add_all([p1, p2, p3, p4])
    await session.flush()

    # 5. Associations
    await session.execute(
        user_roles.insert().values(
            [
                {"user_id": ADMIN_ID, "role_id": ROLE_ADMIN_ID},
                {"user_id": USER_1_ID, "role_id": ROLE_USER_ID},
            ]
        )
    )
    await session.execute(
        role_permissions.insert().values(
            [
                {"role_id": ROLE_ADMIN_ID, "permission_id": p1.id},
                {"role_id": ROLE_ADMIN_ID, "permission_id": p2.id},
                {"role_id": ROLE_USER_ID, "permission_id": p3.id},
                {"role_id": ROLE_USER_ID, "permission_id": p4.id},
            ]
        )
    )
    await session.commit()
