from typing import Optional, Self

from pydantic import ConfigDict
from uuid_extensions import uuid7  # type: ignore[import-untyped]

from domain.entities import BaseEntity
from domain.validators import DescriptionStr, PermissionSlug


class Permission(BaseEntity):
    slug: PermissionSlug
    description: Optional[DescriptionStr]

    model_config = ConfigDict(from_attributes=True)

    @classmethod
    def create(cls, slug: PermissionSlug, description: Optional[DescriptionStr]) -> Self:
        return cls(id=uuid7(), slug=slug, description=description)
