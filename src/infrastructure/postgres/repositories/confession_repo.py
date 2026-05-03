from __future__ import annotations

import asyncio
import logging
from typing import TYPE_CHECKING, Optional

from sqlalchemy import delete, func, select, update

from domain.entities import Confession
from domain.errors import UpdateError
from domain.interfaces.database import IConfessionRepo
from infrastructure.postgres.models import ConfessionModel
from infrastructure.postgres.repositories.base import BaseRepo


logger = logging.getLogger(__name__)

if TYPE_CHECKING:
    from pydantic import UUID7

    from domain.dto import ConfessionUpdateInput


class ConfessionRepo(BaseRepo, IConfessionRepo):
    async def create(self, confession: Confession) -> Confession:
        new_confession = ConfessionModel(
            id=confession.id,
            title=confession.title,
            body=confession.body,
            authored_by=confession.authored_by,
            user_id=confession.user_id,
            created_at=confession.created_at,
        )

        self._session.add(new_confession)
        await self._session.flush()

        return Confession.model_validate(new_confession)

    async def get_one(self, id: UUID7) -> Optional[Confession]:
        stmt = select(ConfessionModel).where(ConfessionModel.id == id)

        result = await self._session.execute(stmt)
        logger.debug("Execute: %s", stmt)

        model = result.unique().scalar_one_or_none()
        if not model:
            return None

        return Confession.model_validate(model)

    async def get_all(
        self, limit: Optional[int] = None, offset: Optional[int] = None
    ) -> tuple[list[Confession], int]:
        stmt = (
            select(ConfessionModel)
            .order_by(ConfessionModel.created_at.desc())
            .limit(limit)
            .offset(offset)
        )
        count_stmt = select(func.count()).select_from(ConfessionModel)

        async with asyncio.TaskGroup() as tg:
            result_task = tg.create_task(self._session.execute(stmt))
            total_result_task = tg.create_task(self._session.execute(count_stmt))

        result = result_task.result()
        total_result = total_result_task.result()

        models = result.scalars().all()
        if not models:
            return [], 0

        total = total_result.scalar_one()

        return [Confession.model_validate(el) for el in models], total

    async def update(self, id: UUID7, update_inp: ConfessionUpdateInput) -> Confession:
        to_update = update_inp.model_dump(exclude_unset=True)

        if not to_update:
            raise UpdateError(f"Nothing to update for {id}")

        stmt = (
            update(ConfessionModel)
            .where(ConfessionModel.id == id)
            .values(**to_update)
            .returning(ConfessionModel)
        )

        result = await self._session.execute(stmt)
        model = result.scalar_one()

        return Confession.model_validate(model)

    async def delete(self, id: UUID7):
        stmt = delete(ConfessionModel).where(ConfessionModel.id == id)
        await self._session.execute(stmt)
