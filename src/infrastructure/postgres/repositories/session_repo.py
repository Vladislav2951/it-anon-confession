from __future__ import annotations

from logging import getLogger
from typing import Optional

from sqlalchemy import delete, select
from sqlalchemy.orm import joinedload, noload

from domain.entities import Session
from domain.interfaces.database import ISessionRepo
from infrastructure.postgres.models import SessionModel
from infrastructure.postgres.repositories.base import BaseRepo


logger = getLogger(__name__)


class SessionRepo(BaseRepo, ISessionRepo):
    async def create(self, session: Session):
        new_session = SessionModel(
            id=session.id,
            user_id=session.user_id,
            expires_at=session.expires_at,
            created_at=session.created_at,
            user_agent=session.user_agent,
            ip_address=session.ip_address,
        )

        self._session.add(new_session)

    async def get_one(self, id: str, with_user: bool = False) -> Optional[Session]:
        stmt = select(SessionModel).where(SessionModel.id == id)

        if with_user:
            stmt = stmt.options(joinedload(SessionModel.user))
        else:
            stmt = stmt.options(noload(SessionModel.user))

        result = await self._session.execute(stmt)
        logger.debug("Execute: %s", stmt)

        session_model = result.scalar_one_or_none()

        if not session_model:
            return None

        return Session.model_validate(session_model)

    async def delete(self, id: str):
        stmt = delete(SessionModel).where(SessionModel.id == id)
        _ = await self._session.execute(stmt)
