from __future__ import annotations

from logging import getLogger
from typing import TYPE_CHECKING, Annotated, Any

from fastapi import Depends, HTTPException, status
from starlette.requests import Request

from core.dependencies import session_srv, user_srv
from domain.errors import AppErrorCode


if TYPE_CHECKING:
    from services import SessionService, UserService


logger = getLogger(__name__)


async def auth_only(
    request: Request,
    user_srv: Annotated[UserService, Depends(user_srv)],
    session_srv: Annotated[SessionService, Depends(session_srv)],
):

    session_id = request.cookies.get("session_id")

    unauthorized_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail={
            "code": AppErrorCode.UNAUTHORIZED,
            "message": "Invalid or expired session",
        },
    )

    if not session_id:
        raise unauthorized_exception

    session = await session_srv.get_one(session_id)
    if not session:
        raise unauthorized_exception

    if session.is_expired():
        # TODO delete?
        # await session_srv.delete(session_id)
        raise unauthorized_exception

    user = await user_srv.get_one(session.user_id)
    if not user:
        raise unauthorized_exception

    request.state.user = user
    request.state.session = session
