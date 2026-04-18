from __future__ import annotations

from typing import Optional

from pydantic import UUID7, BaseModel, EmailStr, SecretStr


# from domain.entities import Permission, Role


class User(BaseModel):
    id: UUID7
    email: EmailStr
    password_hash: SecretStr
    first_name: str
    last_name: str
    father_name: Optional[str]


# class UserDetailed(User):
#     # TODO sessions?
#     roles: list["Role"]
#     permissions: list["Permission"]
