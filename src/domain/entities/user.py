from __future__ import annotations

from datetime import datetime
from typing import Optional

from pydantic import UUID7, BaseModel, EmailStr, SecretStr

from core.validators import NameStr


# from domain.entities import Permission, Role


class User(BaseModel):
    id: UUID7
    email: EmailStr
    password_hash: SecretStr
    first_name: NameStr
    last_name: NameStr
    father_name: Optional[NameStr]
    deleted_at: Optional[datetime] = None


# class UserDetailed(User):
#     # TODO sessions?
#     roles: list["Role"]
#     permissions: list["Permission"]
