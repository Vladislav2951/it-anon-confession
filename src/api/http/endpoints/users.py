from __future__ import annotations

import logging
from typing import TYPE_CHECKING

from fastapi import APIRouter, Depends, HTTPException, Response, status
from fastapi.responses import JSONResponse
from pydantic import UUID7, EmailStr

from api.http.common_exceptions import forbidden, internal_server_error, not_found
from api.http.dto import ChangePasswordDTO, UpdateUserDTO
from api.http.middleware import IdentityContextFactory, auth_only, get_current_user
from api.http.response_models import DataResponse, ErrorResponse, MessageResponse
from core.config import get_settings
from core.dependencies import user_srv
from domain.dto import IdentityContext, UserPublic
from domain.enums import Action
from domain.errors import AppErrorCode, BadLoginError, ForbiddenError, NotFoundError


settings = get_settings()


if TYPE_CHECKING:
    from domain.entities import User
    from services import UserService


logger = logging.getLogger(__name__)

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

business_element_name = "users"


@router.get(
    "/{identifier}",
    summary="Get user by email or ID",
    response_model=DataResponse[UserPublic],
    responses={
        status.HTTP_200_OK: {"description": "Success"},
        status.HTTP_404_NOT_FOUND: {"model": ErrorResponse},
    },
)
async def get_one(
    identifier: EmailStr | UUID7,
    user_srv: UserService = Depends(user_srv),
    identity_ctx: IdentityContext = Depends(
        IdentityContextFactory(business_element_name, Action.READ)
    ),
):
    try:
        if isinstance(identifier, str):
            user = await user_srv.get_one_by_email(identifier, identity_ctx)
        else:
            user = await user_srv.get_one(identifier, identity_ctx)

        return JSONResponse(
            {
                "data": UserPublic.model_validate(user, from_attributes=True).model_dump(
                    mode="json"
                )
            }
        )

    except NotFoundError:
        raise not_found("User not found")
    except ForbiddenError:
        raise forbidden()
    except Exception as e:
        logger.exception("Error during getting user: %s", str(e))
        raise internal_server_error()


@router.get(
    "/",
    summary="Get users",
    response_model=DataResponse[UserPublic],
    responses={status.HTTP_200_OK: {"description": "Success"}},
)
async def get_all(
    user_srv: UserService = Depends(user_srv),
    identity_ctx: IdentityContext = Depends(
        IdentityContextFactory(business_element_name, Action.READ)
    ),
):
    try:
        users = await user_srv.get_all(identity_ctx)
        users_response = [
            UserPublic.model_validate(u, from_attributes=True).model_dump(mode="json")
            for u in users
        ]

        return JSONResponse({"data": users_response})

    except ForbiddenError:
        raise forbidden()
    except Exception as e:
        logger.exception("Error during getting users: %s", str(e))
        raise internal_server_error()


@router.delete(
    "/me",
    summary="Delete self account",
    response_model=MessageResponse,
    responses={status.HTTP_200_OK: {"description": "Success"}},
)
async def delete_self(
    user: User = Depends(get_current_user),
    user_srv: UserService = Depends(user_srv),
    identity_ctx: IdentityContext = Depends(
        IdentityContextFactory(business_element_name, Action.DELETE)
    ),
):
    try:
        await user_srv.soft_delete(user.id, identity_ctx)

        response = JSONResponse({"message": "Account has been deleted"})
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
)
async def update(
    user_id: UUID7,
    update_data: UpdateUserDTO,
    user_srv: UserService = Depends(user_srv),
    identity_ctx: IdentityContext = Depends(
        IdentityContextFactory(business_element_name, Action.UPDATE)
    ),
):
    try:
        user = await user_srv.update(user_id, update_data, identity_ctx)
        return JSONResponse(
            {
                "data": UserPublic.model_validate(user, from_attributes=True).model_dump(
                    mode="json"
                )
            }
        )

    except ForbiddenError:
        raise forbidden()
    except NotFoundError:
        raise not_found("User not found")
    except Exception as e:
        logger.exception("Error during user patch update: %s", str(e))
        raise internal_server_error()


@router.post(
    "/{user_id}/change-password",
    summary="Update user",
    response_model=MessageResponse,
    responses={
        status.HTTP_204_NO_CONTENT: {"description": "Success"},
        status.HTTP_404_NOT_FOUND: {"model": ErrorResponse},
        status.HTTP_422_UNPROCESSABLE_CONTENT: {"description": "Validation error"},
    },
)
async def change_password(
    user_id: UUID7,
    password_data: ChangePasswordDTO,
    user_srv: UserService = Depends(user_srv),
    identity_ctx: IdentityContext = Depends(
        IdentityContextFactory(business_element_name, Action.UPDATE)
    ),
):
    try:
        await user_srv.change_password(
            user_id, password_data.old_password, password_data.password, identity_ctx
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

    except ForbiddenError:
        raise forbidden()
    except NotFoundError:
        raise not_found("User not found")
    except Exception as e:
        logger.exception("Error during user changing password: %s", str(e))
        raise internal_server_error()
