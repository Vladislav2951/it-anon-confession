from __future__ import annotations

from datetime import datetime
from typing import TYPE_CHECKING, Optional, Self

from pydantic import ConfigDict, EmailStr, Field, SecretStr
from uuid_extensions import uuid7  # type: ignore[import-untyped]

from core.security import get_password_hash
from domain.entities import BaseEntity
from domain.validators import BioString, NameStr, NicknameStr, PasswordStr, PermissionSlug


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

    # def add_role(self, role: Role) -> None:
    #     if any(r.id == role.id for r in self.roles):
    #         return
    #     self.roles.append(role)

    # def remove_role(self, role_id: UUID7) -> None:
    #     self.roles = [r for r in self.roles if r.id != role_id]
