from __future__ import annotations

from datetime import datetime
from typing import TYPE_CHECKING
import uuid

from sqlalchemy import TIMESTAMP, UUID, ForeignKey, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from infrastructure.postgres.models.base import Base


if TYPE_CHECKING:
    from infrastructure.postgres.models import UserModel


class ConfessionModel(Base):
    __tablename__ = "confessions"

    id: Mapped[uuid.UUID] = mapped_column(UUID, primary_key=True)
    title: Mapped[str] = mapped_column(String(255), nullable=False)
    body: Mapped[str] = mapped_column(String(2000), nullable=False)
    authored_by: Mapped[str] = mapped_column(String(16), nullable=False)

    user_id: Mapped[uuid.UUID] = mapped_column(
        UUID, ForeignKey("users.id", ondelete="CASCADE"), nullable=False
    )

    created_at: Mapped[datetime] = mapped_column(TIMESTAMP(timezone=True), nullable=False)

    user: Mapped[UserModel] = relationship("UserModel", back_populates="confessions")
