from __future__ import annotations

from datetime import datetime
from typing import Optional, Self

from pydantic import ConfigDict, EmailStr, SecretStr
from uuid_extensions import uuid7  # type: ignore[import-untyped]

from core.security import get_password_hash
from domain.entities import BaseEntity
from domain.validators import BioString, NicknameStr, PasswordStr


class User(BaseEntity):
    email: EmailStr
    password_hash: SecretStr
    nickname: NicknameStr
    bio: Optional[BioString]
    deleted_at: Optional[datetime] = None

    model_config = ConfigDict(from_attributes=True)

    @classmethod
    def create(
        cls,
        email: EmailStr,
        password: PasswordStr,
        nickname: NicknameStr,
        bio: Optional[BioString],
    ) -> Self:
        return cls(
            id=uuid7(),
            email=email,
            password_hash=SecretStr(get_password_hash(password.get_secret_value())),
            nickname=nickname,
            bio=bio,
        )

    def is_active(self) -> bool:
        return self.deleted_at is None
