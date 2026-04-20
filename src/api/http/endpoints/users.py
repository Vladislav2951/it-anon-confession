from __future__ import annotations

import logging
from typing import TYPE_CHECKING
import uuid

from fastapi import APIRouter, Depends, HTTPException, Response, status
from fastapi.responses import JSONResponse
from pydantic import UUID7, EmailStr

from api.http.dto import ChangePasswordDTO, UpdateUserDTO
from api.http.middleware import PermissionRequired, auth_only, get_current_user
from api.http.response_models import DataResponse, ErrorResponse, MessageResponse
from core.config import get_settings
from core.dependencies import user_srv
from domain.dto import UserPublic
from domain.enums import PermissionSlugs
from domain.errors import AppErrorCode, BadLoginError, NotFoundError


settings = get_settings()


if TYPE_CHECKING:
    from domain.entities import User
    from services import UserService


logger = logging.getLogger(__name__)

router = APIRouter(prefix="/users", tags=["Users"], dependencies=[Depends(auth_only)])


@router.get(
    "/{identifier}",
    dependencies=[
        Depends(
            PermissionRequired(
                PermissionSlugs.users_view_self.value,
                PermissionSlugs.users_view_any.value,
            )
        )
    ],
    summary="Get user by email or ID",
    response_model=DataResponse[UserPublic],
    responses={
        status.HTTP_200_OK: {"description": "Success"},
        status.HTTP_401_UNAUTHORIZED: {"model": ErrorResponse},
        status.HTTP_403_FORBIDDEN: {"model": ErrorResponse},
        status.HTTP_500_INTERNAL_SERVER_ERROR: {"model": ErrorResponse},
    },
)
async def get(identifier: EmailStr | UUID7, user_srv: UserService = Depends(user_srv)):
    try:
        if isinstance(identifier, str):
            user = await user_srv.get_one_by_email(identifier)
        else:
            user = await user_srv.get_one(identifier)

        if user:
            return JSONResponse(
                {
                    "data": UserPublic.model_validate(
                        user, from_attributes=True
                    ).model_dump(mode="json")
                }
            )
        else:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail={"code": AppErrorCode.NOT_FOUND, "message": "User not found"},
            )

    except Exception as e:
        logger.exception("Error during self account delete: %s", str(e))
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail={
                "code": AppErrorCode.INTERNAL_SERVER_ERROR,
                "message": "An unexpected error occurred",
            },
        )


@router.delete(
    "/me",
    dependencies=[Depends(PermissionRequired(PermissionSlugs.users_delete_self.value))],
    summary="Delete self account",
    response_model=MessageResponse,
    responses={
        status.HTTP_200_OK: {"description": "Success"},
        status.HTTP_401_UNAUTHORIZED: {"model": ErrorResponse},
        status.HTTP_403_FORBIDDEN: {"model": ErrorResponse},
        status.HTTP_500_INTERNAL_SERVER_ERROR: {"model": ErrorResponse},
    },
)
async def delete_self(
    user: User = Depends(get_current_user), user_srv: UserService = Depends(user_srv)
):
    try:
        await user_srv.soft_delete(user.id, user)

        response = JSONResponse({"message": "Account has been deleted"})
        response.delete_cookie(key="session_id")
        return response

    except Exception as e:
        logger.exception("Error during self account delete: %s", str(e))
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail={
                "code": AppErrorCode.INTERNAL_SERVER_ERROR,
                "message": "An unexpected error occurred",
            },
        )


@router.patch(
    "/{user_id}",
    dependencies=[
        Depends(
            PermissionRequired(
                PermissionSlugs.users_update_self.value,
                PermissionSlugs.users_update_any.value,
            )
        )
    ],
    summary="Update user",
    response_model=DataResponse[UserPublic],
    responses={
        status.HTTP_200_OK: {"description": "Success"},
        status.HTTP_401_UNAUTHORIZED: {"model": ErrorResponse},
        status.HTTP_403_FORBIDDEN: {"model": ErrorResponse},
        status.HTTP_500_INTERNAL_SERVER_ERROR: {"model": ErrorResponse},
    },
)
async def update(
    user_id: UUID7, update_data: UpdateUserDTO, user_srv: UserService = Depends(user_srv)
):
    try:
        user = await user_srv.update(user_id, update_data)
        return JSONResponse(
            {
                "data": UserPublic.model_validate(user, from_attributes=True).model_dump(
                    mode="json"
                )
            }
        )
    except Exception as e:
        logger.exception("Error during user patch update: %s", str(e))
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail={
                "code": AppErrorCode.INTERNAL_SERVER_ERROR,
                "message": "An unexpected error occurred",
            },
        )


@router.post(
    "/{user_id}/change-password",
    dependencies=[Depends(PermissionRequired(PermissionSlugs.users_update_self.value))],
    summary="Update user",
    response_model=MessageResponse,
    responses={
        status.HTTP_204_NO_CONTENT: {"description": "Success"},
        status.HTTP_401_UNAUTHORIZED: {"model": ErrorResponse},
        status.HTTP_404_NOT_FOUND: {"model": ErrorResponse},
        status.HTTP_403_FORBIDDEN: {"model": ErrorResponse},
        status.HTTP_500_INTERNAL_SERVER_ERROR: {"model": ErrorResponse},
    },
)
async def change_password(
    user_id: UUID7,
    password_data: ChangePasswordDTO,
    user_srv: UserService = Depends(user_srv),
):
    try:
        await user_srv.change_password(
            user_id, password_data.old_password, password_data.password
        )
        return Response(status_code=status.HTTP_204_NO_CONTENT)
    except BadLoginError:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_CONTENT,
            detail={
                "code": AppErrorCode.BAD_LOGIN,
                "message": "Incorrect current password",
            },
        )
    except NotFoundError:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail={"code": AppErrorCode.NOT_FOUND, "message": "User not found"},
        )
    except Exception as e:
        logger.exception("Error during user patch update: %s", str(e))
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail={
                "code": AppErrorCode.INTERNAL_SERVER_ERROR,
                "message": "An unexpected error occurred",
            },
        )
