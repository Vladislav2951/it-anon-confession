from datetime import datetime
from typing import Optional

from pydantic import ConfigDict, EmailStr, SecretStr

from domain.entities import BaseEntity, Role
from domain.validators import NameStr, PermissionSlug


class User(BaseEntity):
    email: EmailStr
    password_hash: SecretStr
    first_name: NameStr
    last_name: NameStr
    father_name: Optional[NameStr]
    deleted_at: Optional[datetime] = None

    roles: Optional[list[Role]] = None

    model_config = ConfigDict(from_attributes=True)

    def has_role(self, role: NameStr) -> bool:
        return any(r.name == role for r in (self.roles or []))

    def has_permission(self, permission: PermissionSlug) -> bool:
        return any(
            perm.slug == permission
            for role in (self.roles or [])
            for perm in (role.permissions)
        )
