from __future__ import annotations

from abc import ABC, abstractmethod
from typing import TYPE_CHECKING, Optional


if TYPE_CHECKING:
    from pydantic import UUID7, EmailStr

    from domain.dto import RegisterInput
    from domain.entities import User
    from domain.interfaces.database.filters import UserFilter


class IUserRepo(ABC):
    @abstractmethod
    async def create(self, register_inp: RegisterInput) -> User: ...

    @abstractmethod
    async def get_one_by_email(
        self, email: EmailStr, with_roles: bool = False
    ) -> Optional[User]: ...

    @abstractmethod
    async def get_one(self, id: UUID7, with_roles: bool = False) -> Optional[User]: ...

    @abstractmethod
    async def get_all(
        self, with_roles: bool = False, filter: Optional[UserFilter] = None
    ) -> list[User]: ...

    @abstractmethod
    async def soft_delete(self, id: UUID7): ...
