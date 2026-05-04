from typing import Optional

from pydantic import BaseModel

from domain.entities import User
from domain.enums import Action


class IdentityContext(BaseModel):
    current_user: User
    business_element_name: str
    action: Action
