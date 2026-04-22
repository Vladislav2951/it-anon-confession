"""seed admin, users and permissions

Revision ID: fa6c26a70384
Revises: 283287e86b88
Create Date: 2026-04-21 20:40:38.788254

"""

from datetime import datetime, timezone
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = "fa6c26a70384"
down_revision: Union[str, Sequence[str], None] = "283287e86b88"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


# --- STATIC UUID v7 CONSTANTS ---
# Business Elements
BE_USERS_ID = "019ca1e5-c378-7000-8000-000000000001"
BE_ADMIN_ID = "019ca1e5-c378-7000-8000-000000000002"
BE_CONFESSIONS_ID = "019ca1e5-c378-7000-8000-000000000003"

# Roles
ROLE_ADMIN_ID = "019ca1e5-c378-7000-8000-000000000101"
ROLE_USER_ID = "019ca1e5-c378-7000-8000-000000000102"

# Users
ADMIN_USER_ID = "019ca1e5-c378-7000-8000-000000000201"
USER_1_ID = "019ca1e5-c378-7000-8000-000000000202"
USER_2_ID = "019ca1e5-c378-7000-8000-000000000203"

# Permissions
P_ADMIN_USERS = "019ca1e5-c378-7000-8000-000000000301"
P_ADMIN_ADMIN = "019ca1e5-c378-7000-8000-000000000302"
P_ADMIN_CONFESSIONS = "019ca1e5-c378-7000-8000-000000000303"
P_USER_USERS = "019ca1e5-c378-7000-8000-000000000304"
P_USER_CONFESSIONS = "019ca1e5-c378-7000-8000-000000000305"

# Confessions
CONF_1_ID = "019ca1e5-c378-7000-8000-000000000401"
CONF_2_ID = "019ca1e5-c378-7000-8000-000000000402"
CONF_3_ID = "019ca1e5-c378-7000-8000-000000000403"
CONF_4_ID = "019ca1e5-c378-7000-8000-000000000404"


def upgrade() -> None:
    # Table definitions for data operations
    business_elements = sa.table(
        "business_elements",
        sa.column("id", sa.UUID),
        sa.column("name", sa.String),
        sa.column("description", sa.String),
    )
    roles = sa.table(
        "roles",
        sa.column("id", sa.UUID),
        sa.column("name", sa.String),
        sa.column("is_system", sa.Boolean),
    )
    users = sa.table(
        "users",
        sa.column("id", sa.UUID),
        sa.column("email", sa.String),
        sa.column("password", sa.String),
        sa.column("nickname", sa.String),
        sa.column("bio", sa.String),
        sa.column("deleted_at", sa.TIMESTAMP(timezone=True)),
    )
    user_roles = sa.table(
        "user_roles", sa.column("user_id", sa.UUID), sa.column("role_id", sa.UUID)
    )
    permissions = sa.table(
        "permissions",
        sa.column("id", sa.UUID),
        sa.column("business_element_id", sa.UUID),
        sa.column("read_permission", sa.Boolean),
        sa.column("read_all_permission", sa.Boolean),
        sa.column("create_permission", sa.Boolean),
        sa.column("update_permission", sa.Boolean),
        sa.column("update_all_permission", sa.Boolean),
        sa.column("delete_permission", sa.Boolean),
        sa.column("delete_all_permission", sa.Boolean),
        sa.column("description", sa.String),
    )
    role_permissions = sa.table(
        "role_permissions",
        sa.column("role_id", sa.UUID),
        sa.column("permission_id", sa.UUID),
    )
    confessions = sa.table(
        "confessions",
        sa.column("id", sa.UUID),
        sa.column("title", sa.String),
        sa.column("body", sa.String),
        sa.column("authored_by", sa.String),
        sa.column("user_id", sa.UUID),
        sa.column("created_at", sa.TIMESTAMP(timezone=True)),
    )

    # Business Elements
    op.bulk_insert(
        business_elements,
        [
            {"id": BE_USERS_ID, "name": "users", "description": "Users management"},
            {"id": BE_ADMIN_ID, "name": "admin", "description": "Admin panel"},
            {
                "id": BE_CONFESSIONS_ID,
                "name": "confessions",
                "description": "Confessions management",
            },
        ],
    )

    # Roles
    op.bulk_insert(
        roles,
        [
            {"id": ROLE_ADMIN_ID, "name": "admin", "is_system": True},
            {"id": ROLE_USER_ID, "name": "user", "is_system": True},
        ],
    )

    # Users (Admin + Seed Users)
    op.bulk_insert(
        users,
        [
            {
                "id": ADMIN_USER_ID,
                "email": "admin@example.com",
                "password": "$2b$12$ANfB7EKjY/hncfbXpRjpIOt9EO8DFCpv0b9OXkYnaVBNDjoAZ933.",  # admin123
                "nickname": "admin",
                "bio": "Administrator",
                "deleted_at": None,
            },
            {
                "id": USER_1_ID,
                "email": "python_fan@example.com",
                "password": "$2b$12$ANfB7EKjY/hncfbXpRjpIOt9EO8DFCpv0b9OXkYnaVBNDjoAZ933.",
                "nickname": "python_fan",
                "bio": "Keep calm and import this",
                "deleted_at": None,
            },
            {
                "id": USER_2_ID,
                "email": "bug_hunter@example.com",
                "password": "$2b$12$ANfB7EKjY/hncfbXpRjpIOt9EO8DFCpv0b9OXkYnaVBNDjoAZ933.",
                "nickname": "bug_hunter",
                "bio": "Searching for bugs since 1995",
                "deleted_at": None,
            },
        ],
    )

    # User Roles Mapping
    op.bulk_insert(
        user_roles,
        [
            {"user_id": ADMIN_USER_ID, "role_id": ROLE_ADMIN_ID},
            {"user_id": USER_1_ID, "role_id": ROLE_USER_ID},
            {"user_id": USER_2_ID, "role_id": ROLE_USER_ID},
        ],
    )

    # Permissions
    op.bulk_insert(
        permissions,
        [
            # Admin Permissions
            {
                "id": P_ADMIN_USERS,
                "business_element_id": BE_USERS_ID,
                "read_permission": True,
                "read_all_permission": True,
                "create_permission": True,
                "update_permission": True,
                "update_all_permission": True,
                "delete_permission": True,
                "delete_all_permission": True,
                "description": "Admin: full access to users",
            },
            {
                "id": P_ADMIN_ADMIN,
                "business_element_id": BE_ADMIN_ID,
                "read_permission": True,
                "read_all_permission": True,
                "create_permission": True,
                "update_permission": True,
                "update_all_permission": True,
                "delete_permission": True,
                "delete_all_permission": True,
                "description": "Admin: full access to admin panel",
            },
            {
                "id": P_ADMIN_CONFESSIONS,
                "business_element_id": BE_CONFESSIONS_ID,
                "read_permission": True,
                "read_all_permission": True,
                "create_permission": True,
                "update_permission": True,
                "update_all_permission": True,
                "delete_permission": True,
                "delete_all_permission": True,
                "description": "Admin: full access to confessions",
            },
            # User Permissions
            {
                "id": P_USER_USERS,
                "business_element_id": BE_USERS_ID,
                "read_permission": True,
                "read_all_permission": False,
                "create_permission": False,
                "update_permission": True,
                "update_all_permission": False,
                "delete_permission": False,
                "delete_all_permission": False,
                "description": "User: access to own profile",
            },
            {
                "id": P_USER_CONFESSIONS,
                "business_element_id": BE_CONFESSIONS_ID,
                "read_permission": True,
                "read_all_permission": True,
                "create_permission": True,
                "update_permission": True,
                "update_all_permission": False,
                "delete_permission": True,
                "delete_all_permission": False,
                "description": "User: read all, control only owned",
            },
        ],
    )

    # Role Permissions Mapping
    op.bulk_insert(
        role_permissions,
        [
            {"role_id": ROLE_ADMIN_ID, "permission_id": P_ADMIN_USERS},
            {"role_id": ROLE_ADMIN_ID, "permission_id": P_ADMIN_ADMIN},
            {"role_id": ROLE_ADMIN_ID, "permission_id": P_ADMIN_CONFESSIONS},
            {"role_id": ROLE_USER_ID, "permission_id": P_USER_USERS},
            {"role_id": ROLE_USER_ID, "permission_id": P_USER_CONFESSIONS},
        ],
    )

    # Seed Confessions
    now = datetime.now(timezone.utc)
    op.bulk_insert(
        confessions,
        [
            {
                "id": CONF_1_ID,
                "title": "Случайный Drop",
                "body": "Вчера вместо очистки кэша случайно дропнул таблицу на стейдже. Сказал, что это был тест восстановления.",
                "authored_by": "python_fan",
                "user_id": USER_1_ID,
                "created_at": now,
            },
            {
                "id": CONF_2_ID,
                "title": "Сила лени",
                "body": "Потратил неделю на скрипт, который делает 10-секундную работу. Зато теперь я официально 'автоматизатор'.",
                "authored_by": "python_fan",
                "user_id": USER_1_ID,
                "created_at": now,
            },
            {
                "id": CONF_3_ID,
                "title": "Магия CSS",
                "body": "Я все еще использую !important, когда никто не видит. Простите меня, боги фронтенда.",
                "authored_by": "bug_hunter",
                "user_id": USER_2_ID,
                "created_at": now,
            },
            {
                "id": CONF_4_ID,
                "title": "Legacy боль",
                "body": "Нашел ужасный кусок кода, проклял автора, а потом увидел свой ник в git blame пятилетней давности.",
                "authored_by": "bug_hunter",
                "user_id": USER_2_ID,
                "created_at": now,
            },
        ],
    )


def downgrade() -> None:
    # Delete in reverse order to satisfy FK constraints
    op.execute(
        f"DELETE FROM confessions WHERE id IN ('{CONF_1_ID}', '{CONF_2_ID}', '{CONF_3_ID}', '{CONF_4_ID}')"
    )
    op.execute(
        f"DELETE FROM role_permissions WHERE role_id IN ('{ROLE_ADMIN_ID}', '{ROLE_USER_ID}')"
    )
    op.execute(
        f"DELETE FROM permissions WHERE id IN ('{P_ADMIN_USERS}', '{P_ADMIN_ADMIN}', '{P_ADMIN_CONFESSIONS}', '{P_USER_USERS}', '{P_USER_CONFESSIONS}')"
    )
    op.execute(
        f"DELETE FROM user_roles WHERE user_id IN ('{ADMIN_USER_ID}', '{USER_1_ID}', '{USER_2_ID}')"
    )
    op.execute(
        f"DELETE FROM users WHERE id IN ('{ADMIN_USER_ID}', '{USER_1_ID}', '{USER_2_ID}')"
    )
    op.execute(f"DELETE FROM roles WHERE id IN ('{ROLE_ADMIN_ID}', '{ROLE_USER_ID}')")
    op.execute(
        f"DELETE FROM business_elements WHERE id IN ('{BE_USERS_ID}', '{BE_ADMIN_ID}', '{BE_CONFESSIONS_ID}')"
    )
