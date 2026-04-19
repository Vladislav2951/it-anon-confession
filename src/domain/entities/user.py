from datetime import datetime
from typing import Optional

from pydantic import ConfigDict, EmailStr, SecretStr

from domain.entities import BaseEntity, Role
from domain.validators import NameStr


class User(BaseEntity):
    model_config = ConfigDict(from_attributes=True)

    email: EmailStr
    password_hash: SecretStr
    first_name: NameStr
    last_name: NameStr
    father_name: Optional[NameStr]
    deleted_at: Optional[datetime] = None

    roles: Optional[list[Role]] = None
