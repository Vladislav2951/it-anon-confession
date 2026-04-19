from pydantic import ConfigDict

from domain.entities import BaseEntity
from domain.validators import PermissionSlug


class Permission(BaseEntity):
    model_config = ConfigDict(from_attributes=True)

    slug: PermissionSlug
