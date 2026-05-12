from __future__ import annotations

from abc import ABC, abstractmethod
from typing import TYPE_CHECKING, Optional


if TYPE_CHECKING:
    from pydantic import UUID7

    from domain.dto import RoleUpdateInput
    from domain.entities import Role
    from domain.validators import NameStr


class IRoleRepo(ABC):
    @abstractmethod
    async def create(self, role: Role) -> Role:
        pass

    @abstractmethod
    async def get_one(self, id: UUID7) -> Optional[Role]:
        pass

    @abstractmethod
    async def get_one_by_name(self, name: NameStr) -> Optional[Role]:
        pass

    @abstractmethod
    async def get_all(
        self, limit: Optional[int] = None, offset: Optional[int] = None
    ) -> list[Role]:
        pass

    @abstractmethod
    async def count(self) -> int:
        pass

    @abstractmethod
    async def update(self, id: UUID7, update_inp: RoleUpdateInput) -> Role:
        pass

    @abstractmethod
    async def delete(self, id: UUID7):
        pass

    @abstractmethod
    async def get_user_roles(self, user_id: UUID7) -> list[Role]:
        pass

    @abstractmethod
    async def assign_permission(self, role_id: UUID7, permission_id: UUID7):
        pass

    @abstractmethod
    async def revoke_permission(self, role_id: UUID7, permission_id: UUID7):
        pass
