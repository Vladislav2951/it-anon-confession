from __future__ import annotations

from typing import TYPE_CHECKING
import uuid

from sqlalchemy import UUID, String
from sqlalchemy.orm import Mapped, mapped_column, relationship
from uuid_extensions import uuid7  # type: ignore[import-untyped]

from infrastructure.postgres.models.base import Base


if TYPE_CHECKING:
    from infrastructure.postgres.models import PermissionModel, UserModel


class RoleModel(Base):
    __tablename__ = "roles"

    id: Mapped[uuid.UUID] = mapped_column(UUID, primary_key=True, default=uuid7)
    name: Mapped[str] = mapped_column(String(50), unique=True)

    users: Mapped[list[UserModel]] = relationship(
        secondary="user_roles", back_populates="roles", lazy="raise"
    )

    permissions: Mapped[list[PermissionModel]] = relationship(
        secondary="role_permissions", back_populates="roles", lazy="raise"
    )
