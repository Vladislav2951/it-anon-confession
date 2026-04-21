from __future__ import annotations

from abc import ABC, abstractmethod
from typing import TYPE_CHECKING, Optional


if TYPE_CHECKING:
    from pydantic import UUID7, EmailStr

    from domain.dto import ChangePasswordUserInput, PatchUpdateUserInput, RegisterInput
    from domain.entities import User
    from domain.interfaces.database.filters import UserFilter


class IUserRepo(ABC):
    @abstractmethod
    async def create(self, create_inp: RegisterInput) -> User: ...

    @abstractmethod
    async def get_one_by_email(self, email: EmailStr) -> Optional[User]: ...

    @abstractmethod
    async def get_one(self, id: UUID7) -> Optional[User]: ...

    @abstractmethod
    async def get_all(
        self, with_roles: bool = False, filter: Optional[UserFilter] = None
    ) -> list[User]: ...

    @abstractmethod
    async def update(
        self, id: UUID7, update_inp: ChangePasswordUserInput | PatchUpdateUserInput
    ) -> User: ...

    @abstractmethod
    async def soft_delete(self, id: UUID7): ...

    @abstractmethod
    async def add_role(self, user_id: UUID7, role_id: UUID7): ...
