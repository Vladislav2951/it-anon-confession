from __future__ import annotations

from datetime import datetime
from typing import TYPE_CHECKING
import uuid

from sqlalchemy import TIMESTAMP, UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship
from uuid_extensions import uuid7  # type: ignore[import-untyped]

from infrastructure.postgres.models.base import Base


if TYPE_CHECKING:
    from infrastructure.postgres.models import RoleModel, SessionModel


class UserModel(Base):
    __tablename__ = "users"

    id: Mapped[uuid.UUID] = mapped_column(UUID, primary_key=True, default=uuid7)
    email: Mapped[str] = mapped_column(unique=True, nullable=False)
    password_hash: Mapped[str] = mapped_column("password", nullable=False)
    first_name: Mapped[str] = mapped_column(nullable=False)
    last_name: Mapped[str] = mapped_column(nullable=False)
    father_name: Mapped[str] = mapped_column(nullable=True)
    deleted_at: Mapped[datetime] = mapped_column(TIMESTAMP(timezone=True), nullable=True)

    roles: Mapped[list[RoleModel]] = relationship(
        secondary="user_roles", back_populates="users", lazy="raise_on_sql"
    )

    sessions: Mapped[list[SessionModel]] = relationship(
        "SessionModel", back_populates="user", cascade="all, delete-orphan"
    )
