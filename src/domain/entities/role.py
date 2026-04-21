from __future__ import annotations

from typing import Self

from pydantic import ConfigDict
from uuid_extensions import uuid7  # type: ignore[import-untyped]

from domain.entities import BaseEntity
from domain.validators import NameStr


class Role(BaseEntity):
    name: NameStr

    is_system: bool = False

    model_config = ConfigDict(from_attributes=True)

    @classmethod
    def create(cls, name: NameStr) -> Self:
        return cls(id=uuid7(), name=name)
