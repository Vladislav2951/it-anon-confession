from typing import Optional

from pydantic import ConfigDict

from domain.entities import BaseEntity, Permission
from domain.validators import NameStr


class Role(BaseEntity):
    name: NameStr

    permissions: Optional[list[Permission]] = None
    is_system: bool = False

    model_config = ConfigDict(from_attributes=True)
