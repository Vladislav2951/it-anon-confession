from __future__ import annotations

from datetime import datetime, timedelta, timezone
import secrets
from typing import TYPE_CHECKING, Optional

from pydantic import UUID7, BaseModel, ConfigDict, Field


if TYPE_CHECKING:
    from domain.entities import User


class Session(BaseModel):
    id: str
    user_id: UUID7
    expires_at: datetime
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))

    user_agent: str | None = None
    ip_address: str | None = None

    model_config = ConfigDict(from_attributes=True)

    def is_expired(self) -> bool:
        return datetime.now(timezone.utc) >= self.expires_at

    @classmethod
    def create(
        cls,
        user_id: UUID7,
        expires_in_seconds: int,
        user_agent: str | None = None,
        ip_address: str | None = None,
    ) -> Session:
        now = datetime.now(timezone.utc)
        return cls(
            id=secrets.token_urlsafe(64),
            user_id=user_id,
            created_at=now,
            expires_at=now + timedelta(seconds=expires_in_seconds),
            user_agent=user_agent,
            ip_address=ip_address,
        )
