from typing import Optional

from pydantic import ConfigDict

from domain.entities import BaseEntity
from domain.validators import DescriptionStr, NameStr


class BusinessElement(BaseEntity):
    name: NameStr
    description: Optional[DescriptionStr] = None

    model_config = ConfigDict(from_attributes=True)
