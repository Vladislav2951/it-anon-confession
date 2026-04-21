from __future__ import annotations

import logging
from typing import TYPE_CHECKING

from fastapi import Depends
from starlette.requests import Request

from api.http.common_exceptions import unauthorized
from core.dependencies import session_srv, user_srv
from domain.dto import IdentityContext
from domain.enums import Action


if TYPE_CHECKING:
    from domain.entities import User
    from services import SessionService, UserService


logger = logging.getLogger(__name__)


async def auth_only(
    request: Request,
    user_srv: UserService = Depends(user_srv),
    session_srv: SessionService = Depends(session_srv),
):

    session_id = request.cookies.get("session_id")

    if not session_id:
        raise unauthorized

    session = await session_srv.get_one(session_id)
    if not session:
        raise unauthorized

    if session.is_expired():
        await session_srv.delete(session_id)
        raise unauthorized

    identity_ctx = IdentityContext(
        current_user=None, business_element_name="__system__", action=Action.READ
    )
    user: User | None = await user_srv.get_one(session.user_id, identity_ctx)
    if not user:
        raise unauthorized

    request.state.user = user
    request.state.session = session
