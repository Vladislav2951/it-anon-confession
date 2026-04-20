from __future__ import annotations

import logging
from typing import TYPE_CHECKING, Optional

from core.security import get_token_hash
from domain.entities import Session


logger = logging.getLogger(__name__)


if TYPE_CHECKING:
    from domain.interfaces.database.uow import IDatabaseTransactionFactory


class SessionService:
    def __init__(self, db_transaction_factory: IDatabaseTransactionFactory):
        self._db_transaction_factory = db_transaction_factory

    async def save(self, session: Session):
        async with self._db_transaction_factory() as t:
            await t.session_repo.create(session)

    async def get_one(self, raw_id: str) -> Optional[Session]:
        session_id_hash = get_token_hash(raw_id)
        async with self._db_transaction_factory() as t:
            return await t.session_repo.get_one(session_id_hash)

    async def delete(self, raw_id: str):
        session_id_hash = get_token_hash(raw_id)
        async with self._db_transaction_factory() as t:
            return await t.session_repo.delete(session_id_hash)
