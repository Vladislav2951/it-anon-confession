from __future__ import annotations

from typing import TYPE_CHECKING, Optional
import uuid

from sqlalchemy import UUID, String
from sqlalchemy.orm import Mapped, mapped_column, relationship
from uuid_extensions import uuid7  # type: ignore[import-untyped]

from infrastructure.postgres.models.base import Base


if TYPE_CHECKING:
    from infrastructure.postgres.models import RoleModel


class PermissionModel(Base):
    __tablename__ = "permissions"

    id: Mapped[uuid.UUID] = mapped_column(UUID, primary_key=True, default=uuid7)
    slug: Mapped[str] = mapped_column(String(64), unique=True)
    description: Mapped[Optional[str]] = mapped_column(String(250), nullable=True)

    roles: Mapped[list[RoleModel]] = relationship(
        secondary="role_permissions", back_populates="permissions", lazy="raise_on_sql"
    )
