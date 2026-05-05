from __future__ import annotations

from typing import TYPE_CHECKING, Optional
import uuid

from sqlalchemy import UUID, Boolean, ForeignKey, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from infrastructure.postgres.models.base import Base


if TYPE_CHECKING:
    from infrastructure.postgres.models import BusinessElementModel, RoleModel


class PermissionModel(Base):
    __tablename__ = "permissions"

    id: Mapped[uuid.UUID] = mapped_column(UUID, primary_key=True)

    business_element_id: Mapped[int] = mapped_column(
        ForeignKey("business_elements.id", ondelete="CASCADE"), nullable=False
    )

    create_permission: Mapped[bool] = mapped_column(
        Boolean, default=False, nullable=False
    )
    read_permission: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    update_permission: Mapped[bool] = mapped_column(
        Boolean, default=False, nullable=False
    )

    delete_permission: Mapped[bool] = mapped_column(
        Boolean, default=False, nullable=False
    )

    read_own_permission: Mapped[bool] = mapped_column(
        Boolean, default=False, nullable=False
    )
    update_own_permission: Mapped[bool] = mapped_column(
        Boolean, default=False, nullable=False
    )

    delete_own_permission: Mapped[bool] = mapped_column(
        Boolean, default=False, nullable=False
    )

    description: Mapped[Optional[str]] = mapped_column(String(250), nullable=True)

    roles: Mapped[list[RoleModel]] = relationship(
        secondary="role_permissions", back_populates="permissions", lazy="raise_on_sql"
    )

    business_element: Mapped[BusinessElementModel] = relationship(
        back_populates="permissions", lazy="raise_on_sql"
    )
