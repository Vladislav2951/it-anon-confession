from __future__ import annotations

from typing import TYPE_CHECKING, Optional
import uuid

from sqlalchemy import UUID, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from infrastructure.postgres.models.base import Base


if TYPE_CHECKING:
    from infrastructure.postgres.models import PermissionModel


class BusinessElementModel(Base):
    __tablename__ = "business_elements"

    id: Mapped[uuid.UUID] = mapped_column(UUID, primary_key=True)
    name: Mapped[str] = mapped_column(String(64), unique=True, nullable=False)
    description: Mapped[str | None] = mapped_column(String(250), nullable=True)

    permissions: Mapped[list[PermissionModel]] = relationship(
        "PermissionModel", back_populates="business_element", cascade="all, delete-orphan"
    )
