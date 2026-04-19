from __future__ import annotations

from logging import getLogger
from typing import TYPE_CHECKING, Optional

from domain.entities import User
from domain.errors import NotFoundError


if TYPE_CHECKING:
    from pydantic import EmailStr

logger = getLogger(__name__)


if TYPE_CHECKING:
    from domain.interfaces.database.uow import IDatabaseUoWFactory


class UserService:
    def __init__(self, db_uow_factory: IDatabaseUoWFactory):
        self._db_uow_factory = db_uow_factory

    async def get_one_by_email(self, email: EmailStr) -> Optional[User]:
        uow = self._db_uow_factory()
        return await uow.user_repo.get_one_by_email(email)
