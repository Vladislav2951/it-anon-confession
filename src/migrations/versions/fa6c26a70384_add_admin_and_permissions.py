"""add admin and permissions

Revision ID: fa6c26a70384
Revises: 283287e86b88
Create Date: 2026-04-21 20:40:38.788254

"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from uuid_extensions import uuid7  # type: ignore[import-untyped]


# revision identifiers, used by Alembic.
revision: str = "fa6c26a70384"
down_revision: Union[str, Sequence[str], None] = "283287e86b88"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    # Генерируем ID
    be_users_id = uuid7()
    be_admin_id = uuid7()
    be_confessions_id = uuid7()

    role_admin_id = uuid7()
    role_user_id = uuid7()

    admin_user_id = uuid7()

    # Бизнес элементы
    business_elements = sa.table(
        "business_elements",
        sa.column("id", sa.UUID),
        sa.column("name", sa.String),
        sa.column("description", sa.String),
    )
    op.bulk_insert(
        business_elements,
        [
            {"id": be_users_id, "name": "users", "description": "Users management"},
            {"id": be_admin_id, "name": "admin", "description": "Admin panel"},
            {
                "id": be_confessions_id,
                "name": "confessions",
                "description": "Confessions",
            },
        ],
    )

    # Роли
    roles = sa.table(
        "roles",
        sa.column("id", sa.UUID),
        sa.column("name", sa.String),
        sa.column("is_system", sa.Boolean),
    )
    op.bulk_insert(
        roles,
        [
            {"id": role_admin_id, "name": "admin", "is_system": True},
            {"id": role_user_id, "name": "user", "is_system": True},
        ],
    )

    # Администратор
    users = sa.table(
        "users",
        sa.column("id", sa.UUID),
        sa.column("email", sa.String),
        sa.column("password", sa.String),
        sa.column("nickname", sa.String),
        sa.column("bio", sa.String),
        sa.column("deleted_at", sa.TIMESTAMP),
    )
    op.bulk_insert(
        users,
        [
            {
                "id": admin_user_id,
                "email": "admin@example.com",
                "password": "$2b$12$ANfB7EKjY/hncfbXpRjpIOt9EO8DFCpv0b9OXkYnaVBNDjoAZ933.",  # admin123
                "nickname": "admin",
                "bio": "Administrator",
                "deleted_at": None,
            }
        ],
    )

    # Назначение роли администратору
    user_roles = sa.table(
        "user_roles", sa.column("user_id", sa.UUID), sa.column("role_id", sa.UUID)
    )
    op.bulk_insert(user_roles, [{"user_id": admin_user_id, "role_id": role_admin_id}])

    # Права доступа
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

    # ID для связок прав с ролями
    p_admin_users = uuid7()
    p_admin_admin = uuid7()
    p_admin_confessions = uuid7()
    p_user_users = uuid7()
    p_user_confessions = uuid7()

    op.bulk_insert(
        permissions,
        [
            # Права admin: Всё True
            {
                "id": p_admin_users,
                "business_element_id": be_users_id,
                "read_permission": True,
                "read_all_permission": True,
                "create_permission": True,
                "update_permission": True,
                "update_all_permission": True,
                "delete_permission": True,
                "delete_all_permission": True,
                "description": "Admin: full access to users (except delete himself)",
            },
            {
                "id": p_admin_admin,
                "business_element_id": be_admin_id,
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
                "id": p_admin_confessions,
                "business_element_id": be_confessions_id,
                "read_permission": True,
                "read_all_permission": True,
                "create_permission": True,
                "update_permission": True,
                "update_all_permission": True,
                "delete_permission": True,
                "delete_all_permission": True,
                "description": "Admin: full access to confessions",
            },
            # Права user:
            {
                "id": p_user_users,
                "business_element_id": be_users_id,
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
                "id": p_user_confessions,
                "business_element_id": be_confessions_id,
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

    # Роли и Права
    role_permissions = sa.table(
        "role_permissions",
        sa.column("role_id", sa.UUID),
        sa.column("permission_id", sa.UUID),
    )
    op.bulk_insert(
        role_permissions,
        [
            # Связи admin
            {"role_id": role_admin_id, "permission_id": p_admin_users},
            {"role_id": role_admin_id, "permission_id": p_admin_admin},
            {"role_id": role_admin_id, "permission_id": p_admin_confessions},
            # Связи user
            {"role_id": role_user_id, "permission_id": p_user_users},
            {"role_id": role_user_id, "permission_id": p_user_confessions},
        ],
    )


def downgrade() -> None:
    """Downgrade schema."""
    op.execute("DELETE FROM role_permissions")
    op.execute("DELETE FROM user_roles")
    op.execute("DELETE FROM permissions")
    op.execute("DELETE FROM users")
    op.execute("DELETE FROM roles")
    op.execute("DELETE FROM business_elements")
