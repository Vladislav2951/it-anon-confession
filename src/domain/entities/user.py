from datetime import datetime
from typing import Optional

from pydantic import ConfigDict, EmailStr, SecretStr

from domain.entities import BaseEntity, Role
from domain.validators import BioString, NameStr, NicknameStr, PermissionSlug


class User(BaseEntity):
    email: EmailStr
    nickname: NicknameStr
    bio: Optional[BioString]
    password_hash: SecretStr
    deleted_at: Optional[datetime] = None

    roles: list[Role] = []

    model_config = ConfigDict(from_attributes=True)

    def has_role(self, role: NameStr) -> bool:
        return any(r.name == role for r in (self.roles or []))

    def has_permission(self, permission: PermissionSlug) -> bool:
        return any(
            perm.slug == permission
            for role in (self.roles or [])
            for perm in (role.permissions)
        )
