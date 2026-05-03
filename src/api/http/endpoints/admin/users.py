from __future__ import annotations

import logging
from typing import TYPE_CHECKING, Annotated

from fastapi import APIRouter, Depends, Query, Response, status
from fastapi.responses import JSONResponse
from pydantic import UUID7

from api.http.common_exceptions import (
    conflict,
    forbidden,
    internal_server_error,
    not_found,
)
from api.http.dto import PaginationDTO, UserPublic
from api.http.middleware import IdentityContextFactory, auth_only
from api.http.response_models import (
    DataManyResponse,
    DataResponse,
    ErrorResponse,
    MessageResponse,
    Meta,
)
from core.config import get_settings
from core.dependencies import user_srv
from domain.entities import Permission
from domain.enums import Action
from domain.errors import ConflictError, ForbiddenError, NotFoundError


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


@router.get(
    "/",
    summary="Get users",
    response_model=DataManyResponse[UserPublic],
    responses={status.HTTP_200_OK: {"description": "Success"}},
)
async def get_all(
    pagination: Annotated[PaginationDTO, Query()],
    user_srv: UserService = Depends(user_srv),
    identity_ctx: IdentityContext = Depends(
        IdentityContextFactory(business_element_name, Action.READ)
    ),
):
    try:
        users, total = await user_srv.get_all(
            identity_ctx, pagination.limit, pagination.offset
        )

        data = [
            UserPublic.model_validate(u, from_attributes=True).model_dump(mode="json")
            for u in users
        ]
        meta = Meta(page=pagination.page, size=pagination.size, total_items=total)

        return {"data": data, "meta": meta}

    except ForbiddenError:
        raise forbidden()
    except Exception as e:
        logger.exception("Error during getting users: %s", str(e))
        raise internal_server_error()


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
        raise forbidden("Are you trying to remove yourself?")

    except Exception as e:
        logger.exception("Error during deleting account: %s", str(e))
        raise internal_server_error()


@router.get(
    "/{user_id}/permissions",
    summary="Get all user permissions",
    response_model=DataResponse[list[Permission]],
    responses={
        status.HTTP_200_OK: {"description": "Success"},
        status.HTTP_404_NOT_FOUND: {"model": ErrorResponse},
    },
)
async def get_user_permissions(
    user_id: UUID7,
    user_srv: UserService = Depends(user_srv),
    identity_ctx: IdentityContext = Depends(
        IdentityContextFactory(business_element_name, Action.READ)
    ),
):
    try:
        permissions = await user_srv.get_user_permissions(user_id, identity_ctx)
        data = [p.model_dump(mode="json") for p in permissions]
        return JSONResponse({"data": data})

    except NotFoundError as e:
        raise not_found("User not found")
    except ForbiddenError:
        raise forbidden()
    except Exception as e:
        logger.exception("Error during fetching user permissions: %s", str(e))
        raise internal_server_error()


@router.post(
    "/{user_id}/assign-role/{role_id}",
    summary="Assign role to user",
    responses={status.HTTP_204_NO_CONTENT: {"description": "Success"}},
)
async def assign_role(
    user_id: UUID7,
    role_id: UUID7,
    user_srv: UserService = Depends(user_srv),
    identity_ctx: IdentityContext = Depends(
        IdentityContextFactory(business_element_name, Action.UPDATE)
    ),
):
    try:
        await user_srv.assign_role(user_id, role_id, identity_ctx)
        return Response(status_code=status.HTTP_204_NO_CONTENT)

    except NotFoundError as e:
        raise not_found(str(e))
    except ConflictError as e:
        raise conflict(str(e))
    except ForbiddenError:
        raise forbidden()
    except Exception as e:
        logger.exception("Error during assigning role: %s", str(e))
        raise internal_server_error()


@router.post(
    "/{user_id}/revoke-role/{role_id}",
    summary="Revoke role from user",
    responses={status.HTTP_204_NO_CONTENT: {"description": "Success"}},
)
async def revoke_role(
    user_id: UUID7,
    role_id: UUID7,
    user_srv: UserService = Depends(user_srv),
    identity_ctx: IdentityContext = Depends(
        IdentityContextFactory(business_element_name, Action.UPDATE)
    ),
):
    try:
        await user_srv.revoke_role(user_id, role_id, identity_ctx)
        return Response(status_code=status.HTTP_204_NO_CONTENT)

    except NotFoundError as e:
        raise not_found(str(e))
    except ForbiddenError as e:
        raise forbidden(str(e))
    except Exception as e:
        logger.exception("Error during revoking role: %s", str(e))
        raise internal_server_error()
