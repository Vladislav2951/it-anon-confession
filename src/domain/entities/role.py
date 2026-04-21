from __future__ import annotations

from typing import TYPE_CHECKING, Self

from pydantic import ConfigDict
from uuid_extensions import uuid7  # type: ignore[import-untyped]

from domain.entities import BaseEntity
from domain.validators import NameStr


if TYPE_CHECKING:
    from domain.entities import Permission


class Role(BaseEntity):
    name: NameStr

    # permissions: list[Permission] = []
    is_system: bool = False

    model_config = ConfigDict(from_attributes=True)

    @classmethod
    def create(cls, name: NameStr) -> Self:
        return cls(id=uuid7(), name=name)
