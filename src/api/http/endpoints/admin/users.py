from __future__ import annotations

import logging
from typing import TYPE_CHECKING

from fastapi import APIRouter, Depends, HTTPException, Response, status
from fastapi.responses import JSONResponse
from pydantic import UUID7

from api.http.common_exceptions import internal_server_error
from api.http.middleware import IdentityContextFactory, auth_only
from api.http.response_models import ErrorResponse, MessageResponse
from core.config import get_settings
from core.dependencies import user_srv
from domain.enums import Action
from domain.errors import AppErrorCode, ForbiddenError


settings = get_settings()


if TYPE_CHECKING:
    from domain.dto import IdentityContext
    from services import UserService


logger = logging.getLogger(__name__)

router = APIRouter(
    prefix="/users",
    tags=["Users"],
    dependencies=[Depends(auth_only)],
    responses={
        status.HTTP_401_UNAUTHORIZED: {"model": ErrorResponse},
        status.HTTP_403_FORBIDDEN: {"model": ErrorResponse},
        status.HTTP_422_UNPROCESSABLE_CONTENT: {"description": "Validation error"},
        status.HTTP_500_INTERNAL_SERVER_ERROR: {"model": ErrorResponse},
    },
)
business_element_name = "admin"


@router.delete(
    "/{user_id}",
    summary="Delete account",
    response_model=MessageResponse,
    responses={status.HTTP_204_NO_CONTENT: {"description": "Success"}},
)
async def delete(
    user_id: UUID7,
    user_srv: UserService = Depends(user_srv),
    identity_ctx: IdentityContext = Depends(
        IdentityContextFactory(business_element_name, Action.DELETE)
    ),
):
    try:
        await user_srv.soft_delete(user_id, identity_ctx)

        response = Response(status_code=status.HTTP_204_NO_CONTENT)
        response.delete_cookie(key="session_id")
        return response

    except ForbiddenError:
        logger.warning(
            "An attempt by the last administrator (%s) to delete himself was detected",
            user_id,
        )
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail={
                "code": AppErrorCode.FORBIDDEN,
                "message": "Are you trying to remove yourself?",
            },
        )

    except Exception as e:
        logger.exception("Error during deleting account: %s", str(e))
        raise internal_server_error
