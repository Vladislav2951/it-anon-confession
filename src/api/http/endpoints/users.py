from __future__ import annotations

import logging
from typing import TYPE_CHECKING

from fastapi import APIRouter, Depends, HTTPException, Response, status
from fastapi.responses import JSONResponse
from pydantic import UUID7, EmailStr

from api.http.common_exceptions import (
    conflict,
    forbidden,
    internal_server_error,
    not_found,
)
from api.http.dto import ChangePasswordDTO, UpdateUserDTO, UserPublic
from api.http.middleware import PermissionChecker, auth_only, get_current_user
from api.http.response_models import DataResponse, ErrorResponse, MessageResponse
from core.config import get_settings
from core.dependencies import user_srv
from domain.enums import Action
from domain.errors import (
    AppErrorCode,
    BadLoginError,
    ConflictError,
    ForbiddenError,
    NotFoundError,
)


settings = get_settings()


if TYPE_CHECKING:
    from domain.entities import User
    from services import UserService


logger = logging.getLogger(__name__)

business_element_name = "users"

router = APIRouter(
    prefix="/users",
    tags=["Users"],
    dependencies=[Depends(auth_only)],
    responses={
        status.HTTP_401_UNAUTHORIZED: {"model": ErrorResponse},
        status.HTTP_403_FORBIDDEN: {"model": ErrorResponse},
        status.HTTP_500_INTERNAL_SERVER_ERROR: {"model": ErrorResponse},
    },
)


@router.get(
    "/{identifier}",
    summary="Get user by email or ID",
    response_model=DataResponse[UserPublic],
    responses={
        status.HTTP_200_OK: {"description": "Success"},
        status.HTTP_404_NOT_FOUND: {"model": ErrorResponse},
    },
    dependencies=[Depends(PermissionChecker(business_element_name, Action.READ))],
)
async def get_one(
    identifier: EmailStr | UUID7, user_srv: UserService = Depends(user_srv)
):
    try:
        if isinstance(identifier, str):
            user = await user_srv.get_one_by_email(identifier)
        else:
            user = await user_srv.get_one(identifier)

        return JSONResponse(
            {
                "data": UserPublic.model_validate(user, from_attributes=True).model_dump(
                    mode="json"
                )
            }
        )

    except NotFoundError:
        raise not_found("User not found")
    # except ForbiddenError:
    #     raise forbidden()
    except Exception as e:
        logger.exception("Error during getting user: %s", str(e))
        raise internal_server_error()


@router.delete(
    "/me",
    summary="Delete self account",
    responses={status.HTTP_204_NO_CONTENT: {"description": "Success"}},
    dependencies=[Depends(PermissionChecker(business_element_name, Action.DELETE))],
)
async def delete_self(
    user_srv: UserService = Depends(user_srv),
    current_user: User = Depends(get_current_user),
):
    try:
        await user_srv.soft_delete(current_user.id, current_user)

        response = Response(status_code=status.HTTP_204_NO_CONTENT)
        response.delete_cookie(key="session_id")
        return response

    except ForbiddenError:
        raise forbidden()
    except Exception as e:
        logger.exception("Error during self account delete: %s", str(e))
        raise internal_server_error()


@router.patch(
    "/{user_id}",
    summary="Update user",
    response_model=DataResponse[UserPublic],
    responses={
        status.HTTP_200_OK: {"description": "Success"},
        status.HTTP_404_NOT_FOUND: {"model": ErrorResponse},
    },
    dependencies=[Depends(PermissionChecker(business_element_name, Action.UPDATE))],
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

    except NotFoundError:
        raise not_found("User not found")
    except ConflictError:
        raise conflict("User with suck email or nickname is already exist")
    except Exception as e:
        logger.exception("Error during user patch update: %s", str(e))
        raise internal_server_error()


@router.post(
    "/me/change-password",
    summary="Update user",
    response_model=MessageResponse,
    responses={
        status.HTTP_204_NO_CONTENT: {"description": "Success"},
        status.HTTP_404_NOT_FOUND: {"model": ErrorResponse},
        status.HTTP_422_UNPROCESSABLE_CONTENT: {"description": "Validation error"},
    },
    dependencies=[Depends(PermissionChecker(business_element_name, Action.UPDATE))],
)
async def change_password(
    password_data: ChangePasswordDTO,
    user_srv: UserService = Depends(user_srv),
    current_user: User = Depends(get_current_user),
):
    try:
        await user_srv.change_password(
            current_user.id, password_data.old_password, password_data.password
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
        raise not_found("User not found")
    except Exception as e:
        logger.exception("Error during user changing password: %s", str(e))
        raise internal_server_error()
