from __future__ import annotations

import asyncio
import logging
from typing import TYPE_CHECKING, Optional

from sqlalchemy import func, select

from domain.entities import BusinessElement
from domain.interfaces.database import IBusinessElementRepo
from infrastructure.postgres.models import BusinessElementModel
from infrastructure.postgres.repositories.base import BaseRepo


if TYPE_CHECKING:
    from pydantic import UUID7

    from domain.validators import NameStr

logger = logging.getLogger(__name__)


class BusinessElementRepo(BaseRepo, IBusinessElementRepo):
    async def get_one(self, id: UUID7) -> Optional[BusinessElement]:
        stmt = select(BusinessElementModel).where(BusinessElementModel.id == id)

        result = await self._session.execute(stmt)
        logger.debug("Execute: %s", stmt)

        model = result.unique().scalar_one_or_none()
        if not model:
            return None

        return BusinessElement.model_validate(model)

    async def get_one_by_name(self, name: NameStr) -> Optional[BusinessElement]:
        stmt = select(BusinessElementModel).where(BusinessElementModel.name == name)

        result = await self._session.execute(stmt)
        logger.debug("Execute: %s", stmt)

        model = result.unique().scalar_one_or_none()
        if not model:
            return None

        return BusinessElement.model_validate(model)

    async def get_all(
        self, limit: Optional[int] = None, offset: Optional[int] = None
    ) -> tuple[list[BusinessElement], int]:
        stmt = select(BusinessElementModel).limit(limit).offset(offset)
        count_stmt = select(func.count()).select_from(BusinessElementModel)

        async with asyncio.TaskGroup() as tg:
            result_task = tg.create_task(self._session.execute(stmt))
            total_result_task = tg.create_task(self._session.execute(count_stmt))

        result = result_task.result()
        total_result = total_result_task.result()

        models = result.scalars().unique().all()
        if not models:
            return [], 0

        total = total_result.scalar_one()

        return [BusinessElement.model_validate(el) for el in models], total
