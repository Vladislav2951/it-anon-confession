from __future__ import annotations

from datetime import datetime
from typing import TYPE_CHECKING, Optional, Self

from pydantic import ConfigDict, EmailStr, Field, SecretStr
from uuid_extensions import uuid7  # type: ignore[import-untyped]

from core.security import get_password_hash
from domain.entities import BaseEntity
from domain.validators import BioString, NameStr, NicknameStr, PasswordStr, PermissionSlug


if TYPE_CHECKING:
    from domain.entities import Role


class User(BaseEntity):
    email: EmailStr
    password_hash: SecretStr
    nickname: NicknameStr
    bio: Optional[BioString]
    deleted_at: Optional[datetime] = None

    roles: list[Role] = Field(default_factory=list)

    model_config = ConfigDict(from_attributes=True)

    def has_role(self, role: NameStr) -> bool:
        return any(r.name == role for r in (self.roles or []))

    def has_permission(self, permission: PermissionSlug) -> bool:
        return any(
            perm.slug == permission
            for role in (self.roles or [])
            for perm in (role.permissions)
        )

    @classmethod
    def register(
        cls,
        email: EmailStr,
        password: PasswordStr,
        nickname: NicknameStr,
        bio: Optional[BioString],
        roles: list[Role] = [],
    ) -> Self:
        return cls(
            id=uuid7(),
            email=email,
            password_hash=SecretStr(get_password_hash(password.get_secret_value())),
            nickname=nickname,
            bio=bio,
            roles=roles,
        )
