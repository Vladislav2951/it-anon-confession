from __future__ import annotations

from abc import ABC, abstractmethod
from typing import TYPE_CHECKING, Optional


if TYPE_CHECKING:
    from pydantic import EmailStr


if TYPE_CHECKING:
    from domain.dto import RegisterInput
    from domain.entities import User


class IUserRepo(ABC):
    @abstractmethod
    async def create(self, register_inp: RegisterInput) -> User:
        pass

    @abstractmethod
    async def get_one_by_email(self, email: EmailStr) -> Optional[User]:
        pass
