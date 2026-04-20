from __future__ import annotations

import logging
from typing import TYPE_CHECKING

from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.responses import JSONResponse
from pydantic import UUID7

from api.http.middleware import PermissionRequired, auth_only, get_current_user
from api.http.response_models import ErrorResponse, MessageResponse
from core.config import get_settings
from core.dependencies import user_srv
from domain.enums import PermissionSlugs
from domain.errors import AppErrorCode, ForbiddenError


settings = get_settings()


if TYPE_CHECKING:
    from domain.entities import User
    from services import UserService


logger = logging.getLogger(__name__)

router = APIRouter(prefix="/users", tags=["Users"])


@router.delete(
    "/{user_id}",
    dependencies=[
        Depends(auth_only),
        Depends(PermissionRequired(PermissionSlugs.users_delete_any.value)),
    ],
    summary="Delete account",
    response_model=MessageResponse,
    responses={
        status.HTTP_200_OK: {"description": "Success"},
        status.HTTP_401_UNAUTHORIZED: {"model": ErrorResponse},
        status.HTTP_403_FORBIDDEN: {"model": ErrorResponse},
        status.HTTP_500_INTERNAL_SERVER_ERROR: {"model": ErrorResponse},
    },
)
async def delete_user(
    user_id: UUID7,
    user: User = Depends(get_current_user),
    user_srv: UserService = Depends(user_srv),
):
    try:
        await user_srv.soft_delete(user_id, user)

        response = JSONResponse({"message": "Account has been deleted"})
        response.delete_cookie(key="session_id")
        return response

    except ForbiddenError:
        logger.warning("Admin wants to remove his account")
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail={
                "code": AppErrorCode.FORBIDDEN,
                "message": "Are you trying to remove yourself?",
            },
        )

    except Exception as e:
        logger.exception("Error during account delete: %s", str(e))
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail={
                "code": AppErrorCode.INTERNAL_SERVER_ERROR,
                "message": "An unexpected error occurred",
            },
        )
