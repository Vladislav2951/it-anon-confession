from __future__ import annotations

import logging
from typing import TYPE_CHECKING, Optional

from domain.entities import Confession
from domain.errors import NotFoundError


logger = logging.getLogger(__name__)


if TYPE_CHECKING:
    from pydantic import UUID7

    from domain.dto import ConfessionCreateInput, ConfessionUpdateInput, IdentityContext
    from domain.entities import User
    from domain.interfaces.database.uow import IDatabaseTransactionFactory
    from services import AccessService


class ConfessionService:
    """
    Сервис управления признаниями.
    """

    def __init__(
        self,
        db_transaction_factory: IDatabaseTransactionFactory,
        access_srv: AccessService,
    ):
        self._db_transaction_factory = db_transaction_factory
        self.access_srv = access_srv

    async def create(
        self, confession_inp: ConfessionCreateInput, current_user: User
    ) -> Confession:
        confession = Confession.create(
            title=confession_inp.title,
            body=confession_inp.body,
            authored_by=current_user.nickname,
            user_id=current_user.id,
        )

        async with self._db_transaction_factory() as t:
            return await t.confession_repo.create(confession)

    async def get_one(self, id: UUID7) -> Confession:
        async with self._db_transaction_factory() as t:
            confession = await t.confession_repo.get_one(id)
            if not confession:
                raise NotFoundError(f"Confession {id} not found")

            return confession

    async def get_all(
        self, limit: int = 20, offset: Optional[int] = None
    ) -> tuple[list[Confession], int]:
        async with self._db_transaction_factory() as t:
            return await t.confession_repo.get_all(limit, offset)

    async def update(self, id: UUID7, update_inp: ConfessionUpdateInput) -> Confession:
        async with self._db_transaction_factory() as t:
            if not await t.confession_repo.get_one(id):
                raise NotFoundError(f"Confession {id} not found")

            return await t.confession_repo.update(id, update_inp)

    async def delete(self, id: UUID7) -> None:
        async with self._db_transaction_factory() as t:
            if not await t.confession_repo.get_one(id):
                return None

            await t.confession_repo.delete(id)
