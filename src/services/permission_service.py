from __future__ import annotations

import logging
from typing import TYPE_CHECKING, Optional

from domain.errors import NotFoundError


logger = logging.getLogger(__name__)


if TYPE_CHECKING:
    from pydantic import UUID7

    from domain.dto import IdentityContext
    from domain.entities import Permission
    from domain.interfaces.database.uow import IDatabaseTransactionFactory
    from services import AccessService


class PermissionService:
    """
    Сервис для просмотра доступных в системе прав доступа.
    """

    def __init__(
        self,
        db_transaction_factory: IDatabaseTransactionFactory,
        access_srv: AccessService,
    ):
        self._db_transaction_factory = db_transaction_factory
        self.access_srv = access_srv

    async def get_one(self, id: UUID7) -> Permission:
        async with self._db_transaction_factory() as t:
            permission = await t.permission_repo.get_one(id)
            if not permission:
                raise NotFoundError(f"Permission {id} not found")

            return permission

    async def get_all(
        self, limit: int = 20, offset: Optional[int] = None
    ) -> tuple[list[Permission], int]:
        async with self._db_transaction_factory() as t:
            return await t.permission_repo.get_all(limit, offset)
