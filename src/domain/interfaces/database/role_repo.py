from __future__ import annotations

from abc import ABC, abstractmethod
from typing import TYPE_CHECKING, Optional


if TYPE_CHECKING:
    from pydantic import UUID7

    from domain.dto import RoleCreateInput, RoleUpdateInput
    from domain.entities import Role


class IRoleRepo(ABC):
    @abstractmethod
    async def create(self, role_inp: RoleCreateInput) -> Role: ...

    @abstractmethod
    async def get_one(self, id: UUID7) -> Optional[Role]: ...

    @abstractmethod
    async def get_one_by_name(self, name: str) -> Optional[Role]: ...

    @abstractmethod
    async def get_all(self) -> list[Role]: ...

    @abstractmethod
    async def update(self, id: UUID7, update_inp: RoleUpdateInput) -> Role: ...

    @abstractmethod
    async def delete(self, id: UUID7): ...

    @abstractmethod
    async def get_user_roles(self, user_id: UUID7) -> list[Role]: ...
