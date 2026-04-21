"""add admin and permissions

Revision ID: 9398497394ee
Revises: 4fc4f6cba8a9
Create Date: 2026-04-21 01:43:47.437846

"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from uuid_extensions import uuid7  # type: ignore[import-untyped]


# revision identifiers, used by Alembic.
revision: str = "9398497394ee"
down_revision: Union[str, Sequence[str], None] = "4fc4f6cba8a9"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    permissions_table = sa.table(
        "permissions",
        sa.column("id", sa.UUID),
        sa.column("slug", sa.String),
        sa.column("description", sa.String),
    )
    roles_table = sa.table(
        "roles",
        sa.column("id", sa.UUID),
        sa.column("name", sa.String),
        sa.column("is_system", sa.Boolean),
    )
    role_permissions_table = sa.table(
        "role_permissions",
        sa.column("role_id", sa.UUID),
        sa.column("permission_id", sa.UUID),
    )
    users_table = sa.table(
        "users",
        sa.column("id", sa.UUID),
        sa.column("email", sa.String),
        sa.column("password", sa.String),
        sa.column("nickname", sa.String),
        sa.column("bio", sa.String),
        sa.column("deleted_at", sa.TIMESTAMP),
    )
    user_roles_table = sa.table(
        "user_roles", sa.column("user_id", sa.UUID), sa.column("role_id", sa.UUID)
    )

    admin_role_id = uuid7()
    user_role_id = uuid7()

    admin_user_id = uuid7()

    permissions_to_add = [
        {"id": uuid7(), "slug": "users:view:self", "desc": "View yourself"},
        {"id": uuid7(), "slug": "users:view:any", "desc": "View any user"},
        {"id": uuid7(), "slug": "users:update:self", "desc": "Update yourself"},
        {"id": uuid7(), "slug": "users:update:any", "desc": "Update any user"},
        {"id": uuid7(), "slug": "users:delete:self", "desc": "Delete yourself"},
        {"id": uuid7(), "slug": "users:delete:any", "desc": "Delete any user"},
    ]

    op.bulk_insert(
        permissions_table,
        [
            {"id": p["id"], "slug": p["slug"], "description": p["desc"]}
            for p in permissions_to_add
        ],
    )

    op.bulk_insert(
        roles_table,
        [
            {"id": admin_role_id, "name": "admin", "is_system": True},
            {"id": user_role_id, "name": "user", "is_system": True},
        ],
    )

    role_permissions_data = []
    for p in permissions_to_add:
        # Админу все права
        role_permissions_data.append({"role_id": admin_role_id, "permission_id": p["id"]})

        # User только с суффиксом :self
        if p["slug"].endswith(":self"):
            role_permissions_data.append(
                {"role_id": user_role_id, "permission_id": p["id"]}
            )

    op.bulk_insert(role_permissions_table, role_permissions_data)

    op.bulk_insert(
        users_table,
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

    op.bulk_insert(
        user_roles_table, [{"user_id": admin_user_id, "role_id": admin_role_id}]
    )


def downgrade() -> None:
    op.execute("DELETE FROM user_roles")
    op.execute("DELETE FROM users")
    op.execute("DELETE FROM role_permissions")
    op.execute("DELETE FROM roles")
    op.execute("DELETE FROM permissions")
