from __future__ import annotations

from datetime import datetime
from typing import TYPE_CHECKING, Optional
import uuid

from sqlalchemy import TIMESTAMP, UUID, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from infrastructure.postgres.models.base import Base


if TYPE_CHECKING:
    from infrastructure.postgres.models import ConfessionModel, RoleModel, SessionModel


class UserModel(Base):
    __tablename__ = "users"

    id: Mapped[uuid.UUID] = mapped_column(UUID, primary_key=True)
    email: Mapped[str] = mapped_column(unique=True, nullable=False)
    password_hash: Mapped[str] = mapped_column("password", nullable=False)
    nickname: Mapped[str] = mapped_column(String(16), unique=True, nullable=False)
    bio: Mapped[Optional[str]] = mapped_column(String(1000), nullable=True)
    deleted_at: Mapped[datetime] = mapped_column(TIMESTAMP(timezone=True), nullable=True)

    roles: Mapped[list[RoleModel]] = relationship(
        secondary="user_roles", back_populates="users", lazy="joined"
    )

    sessions: Mapped[list[SessionModel]] = relationship(
        "SessionModel", back_populates="user", cascade="all, delete-orphan"
    )

    confessions: Mapped[list[ConfessionModel]] = relationship(
        "ConfessionModel", back_populates="user", cascade="all, delete-orphan"
    )
