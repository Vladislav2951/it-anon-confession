from __future__ import annotations

import logging
from typing import TYPE_CHECKING

from fastapi import APIRouter, Depends, Response, status
from fastapi.responses import JSONResponse
from pydantic import UUID7

from api.http.common_exceptions import (
    conflict,
    forbidden,
    internal_server_error,
    not_found,
)
from api.http.dto import RoleCreateDTO, RoleUpdateDTO
from api.http.middleware import IdentityContextFactory, auth_only
from api.http.response_models import DataResponse, ErrorResponse, MessageResponse
from core.config import get_settings
from core.dependencies import role_srv
from domain.entities import Role
from domain.enums import Action
from domain.errors import ConflictError, ForbiddenError, NotFoundError


settings = get_settings()


if TYPE_CHECKING:
    from domain.dto import IdentityContext
    from services import RoleService


logger = logging.getLogger(__name__)

router = APIRouter(
    prefix="/roles",
    tags=["Roles"],
    dependencies=[Depends(auth_only)],
    responses={
        status.HTTP_401_UNAUTHORIZED: {"model": ErrorResponse},
        status.HTTP_403_FORBIDDEN: {"model": ErrorResponse},
        status.HTTP_500_INTERNAL_SERVER_ERROR: {"model": ErrorResponse},
    },
)
business_element_name = "admin"


@router.post(
    "/",
    summary="Create role",
    response_model=DataResponse[Role],
    responses={status.HTTP_201_CREATED: {"description": "Success"}},
)
async def create(
    data: RoleCreateDTO,
    role_srv: RoleService = Depends(role_srv),
    identity_ctx: IdentityContext = Depends(
        IdentityContextFactory(business_element_name, Action.CREATE)
    ),
):
    try:
        role = await role_srv.create(data, identity_ctx)
        return JSONResponse(
            {"data": role.model_dump(mode="json")}, status_code=status.HTTP_201_CREATED
        )

    except ForbiddenError:
        raise forbidden()
    except ConflictError:
        raise conflict("Role already exists")
    except Exception as e:
        logger.exception("Error during creating role: %s", str(e))
        raise internal_server_error()


@router.get(
    "/{role_id}",
    summary="Get role",
    response_model=DataResponse[Role],
    responses={status.HTTP_200_OK: {"description": "Success"}},
)
async def get_one(
    role_id: UUID7,
    role_srv: RoleService = Depends(role_srv),
    identity_ctx: IdentityContext = Depends(
        IdentityContextFactory(business_element_name, Action.READ)
    ),
):
    try:
        role = await role_srv.get_one(role_id, identity_ctx)
        return JSONResponse({"data": role.model_dump(mode="json")})

    except NotFoundError:
        raise not_found("Role not found")
    except ForbiddenError:
        raise forbidden()
    except Exception as e:
        logger.exception("Error during getting role: %s", str(e))
        raise internal_server_error()


@router.get(
    "/",
    summary="Get roles",
    response_model=DataResponse[list[Role]],
    responses={status.HTTP_200_OK: {"description": "Success"}},
)
async def get_all(
    role_srv: RoleService = Depends(role_srv),
    identity_ctx: IdentityContext = Depends(
        IdentityContextFactory(business_element_name, Action.READ)
    ),
):
    try:
        roles = await role_srv.get_all(identity_ctx)
        roles_response = [u.model_dump(mode="json") for u in roles]

        return JSONResponse({"data": roles_response})

    except ForbiddenError:
        raise forbidden()
    except Exception as e:
        logger.exception("Error during getting role: %s", str(e))
        raise internal_server_error()


@router.patch(
    "/{role_id}",
    summary="Update role",
    response_model=DataResponse[Role],
    responses={status.HTTP_200_OK: {"description": "Success"}},
)
async def update(
    role_id: UUID7,
    update_data: RoleUpdateDTO,
    role_srv: RoleService = Depends(role_srv),
    identity_ctx: IdentityContext = Depends(
        IdentityContextFactory(business_element_name, Action.UPDATE)
    ),
):
    try:
        role = await role_srv.update(role_id, update_data, identity_ctx)
        return JSONResponse({"data": role.model_dump(mode="json")})

    except NotFoundError:
        raise not_found("Role not found")
    except ConflictError as e:
        raise conflict(str(e))
    except ForbiddenError:
        raise forbidden()
    except Exception as e:
        logger.exception("Error during patching role: %s", str(e))
        raise internal_server_error()


@router.delete(
    "/{role_id}",
    summary="Delete role",
    responses={status.HTTP_204_NO_CONTENT: {"description": "Success"}},
)
async def delete(
    role_id: UUID7,
    role_srv: RoleService = Depends(role_srv),
    identity_ctx: IdentityContext = Depends(
        IdentityContextFactory(business_element_name, Action.DELETE)
    ),
):
    try:
        await role_srv.delete(role_id, identity_ctx)

        return Response(status_code=status.HTTP_204_NO_CONTENT)

    except ForbiddenError as e:
        raise forbidden(str(e))
    except Exception as e:
        logger.exception("Error during deleting role: %s", str(e))
        raise internal_server_error()


@router.post(
    "/{role_id}/assign-permission/{permission_id}",
    summary="Assign permission",
    responses={status.HTTP_204_NO_CONTENT: {"description": "Success"}},
)
async def assign_permission(
    role_id: UUID7,
    permission_id: UUID7,
    role_srv: RoleService = Depends(role_srv),
    identity_ctx: IdentityContext = Depends(
        IdentityContextFactory(business_element_name, Action.UPDATE)
    ),
):
    try:
        await role_srv.assign_permission(role_id, permission_id, identity_ctx)
        return Response(status_code=status.HTTP_204_NO_CONTENT)

    except NotFoundError as e:
        raise not_found(str(e))
    except ConflictError as e:
        raise conflict(str(e))
    except ForbiddenError:
        raise forbidden()
    except Exception as e:
        logger.exception("Error during getting role: %s", str(e))
        raise internal_server_error()


@router.post(
    "/{role_id}/revoke-permission/{permission_id}",
    summary="Revoke permission",
    responses={status.HTTP_204_NO_CONTENT: {"description": "Success"}},
)
async def revoke_permission(
    role_id: UUID7,
    permission_id: UUID7,
    role_srv: RoleService = Depends(role_srv),
    identity_ctx: IdentityContext = Depends(
        IdentityContextFactory(business_element_name, Action.UPDATE)
    ),
):
    try:
        await role_srv.revoke_permission(role_id, permission_id, identity_ctx)
        return Response(status_code=status.HTTP_204_NO_CONTENT)

    except NotFoundError as e:
        raise not_found(str(e))
    except ForbiddenError:
        raise forbidden()
    except Exception as e:
        logger.exception("Error during getting role: %s", str(e))
        raise internal_server_error()
