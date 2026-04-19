from pydantic import ConfigDict

from domain.entities import BaseEntity
from domain.validators import PermissionSlug


class Permission(BaseEntity):
    slug: PermissionSlug

    model_config = ConfigDict(from_attributes=True)
