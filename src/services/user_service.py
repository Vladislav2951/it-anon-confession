from __future__ import annotations

from logging import getLogger
from typing import TYPE_CHECKING, Optional

from domain.entities import User


if TYPE_CHECKING:
    from pydantic import EmailStr

logger = getLogger(__name__)


if TYPE_CHECKING:
    from domain.interfaces.database.uow import IDatabaseTransactionFactory


class UserService:
    def __init__(self, db_transaction_factory: IDatabaseTransactionFactory):
        self._db_transaction_factory = db_transaction_factory

    async def get_one_by_email(self, email: EmailStr) -> Optional[User]:
        async with self._db_transaction_factory() as t:
            return await t.user_repo.get_one_by_email(email)
