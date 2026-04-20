from typing import Annotated, Optional

from pydantic import ConfigDict, StringConstraints

from domain.entities import BaseEntity
from domain.validators import PermissionSlug


class Permission(BaseEntity):
    slug: PermissionSlug
    description: Optional[Annotated[str, StringConstraints(min_length=3, max_length=250)]]

    model_config = ConfigDict(from_attributes=True)
