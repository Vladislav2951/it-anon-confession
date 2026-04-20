from __future__ import annotations

import logging
from typing import TYPE_CHECKING, Optional

from domain.entities import Session
from domain.errors import BadLogin


logger = logging.getLogger(__name__)


if TYPE_CHECKING:
    from domain.interfaces.database.uow import IDatabaseTransactionFactory


class SessionService:
    def __init__(self, db_transaction_factory: IDatabaseTransactionFactory):
        self._db_transaction_factory = db_transaction_factory

    async def save(self, session: Session):
        async with self._db_transaction_factory() as t:
            await t.session_repo.create(session)

    async def get_one(self, id: str) -> Optional[Session]:
        async with self._db_transaction_factory() as t:
            return await t.session_repo.get_one(id)

    async def delete(self, id: str):
        async with self._db_transaction_factory() as t:
            return await t.session_repo.delete(id)
