"""init

Revision ID: 11347497560b
Revises:
Create Date: 2026-04-18 20:41:07.807685

"""

from typing import Sequence, Union

from alembic import op


# revision identifiers, used by Alembic.
revision: str = "11347497560b"
down_revision: Union[str, Sequence[str], None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    op.execute(
        """
    CREATE TABLE users (
        id UUID PRIMARY KEY,
        email VARCHAR UNIQUE NOT NULL,
        password VARCHAR NOT NULL,
        first_name VARCHAR NOT NULL,
        last_name VARCHAR NOT NULL,
        father_name VARCHAR,
        deleted_at TIMESTAMP WITH TIME ZONE
    );
    """
    )


def downgrade() -> None:
    """Downgrade schema."""
    op.execute("DROP TABLE users;")
