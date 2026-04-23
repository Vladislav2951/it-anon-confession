from __future__ import annotations

import logging
from typing import TYPE_CHECKING, Optional

from sqlalchemy import select

from domain.entities import BusinessElement
from domain.interfaces.database import IBusinessElementRepo
from infrastructure.postgres.models import BusinessElementModel
from infrastructure.postgres.repositories.base import BaseRepo


logger = logging.getLogger(__name__)

if TYPE_CHECKING:
    from pydantic import UUID7

    from domain.validators import NameStr


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

    async def get_all(self) -> list[BusinessElement]:
        stmt = select(BusinessElementModel)

        result = await self._session.execute(stmt)
        models = result.scalars().unique().all()

        if not models:
            return []

        return [BusinessElement.model_validate(el) for el in models]
