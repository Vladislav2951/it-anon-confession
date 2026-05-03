from __future__ import annotations

from abc import ABC, abstractmethod
from typing import TYPE_CHECKING, Optional


if TYPE_CHECKING:
    from pydantic import UUID7, EmailStr

    from domain.dto import ChangePasswordUserInput, PatchUpdateUserInput
    from domain.entities import Permission, User
    from domain.interfaces.database.filters import UserFilter


class IUserRepo(ABC):
    @abstractmethod
    async def create(self, user: User) -> User:
        pass

    @abstractmethod
    async def get_one_by_email(self, email: EmailStr) -> Optional[User]:
        pass

    @abstractmethod
    async def get_one(self, id: UUID7) -> Optional[User]:
        pass

    @abstractmethod
    async def get_all(
        self,
        filter: Optional[UserFilter] = None,
        limit: Optional[int] = None,
        offset: Optional[int] = None,
    ) -> tuple[list[User], int]:
        pass

    @abstractmethod
    async def update(
        self, id: UUID7, update_inp: ChangePasswordUserInput | PatchUpdateUserInput
    ) -> User:
        pass

    @abstractmethod
    async def soft_delete(self, id: UUID7):
        pass

    @abstractmethod
    async def get_permissions(self, user_id: UUID7) -> list[Permission]:
        pass

    @abstractmethod
    async def assign_role(self, user_id: UUID7, role_id: UUID7):
        pass

    @abstractmethod
    async def revoke_role(self, user_id: UUID7, role_id: UUID7):
        pass
