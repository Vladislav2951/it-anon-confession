from pydantic import ConfigDict

from domain.entities import BaseEntity
from domain.validators import PermissionSlug


class Permission(BaseEntity):
    slug: PermissionSlug
    is_system: bool = False

    model_config = ConfigDict(from_attributes=True)
