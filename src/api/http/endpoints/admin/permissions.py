from __future__ import annotations

import logging
from typing import TYPE_CHECKING

from fastapi import APIRouter, Depends, status
from fastapi.responses import JSONResponse
from pydantic import UUID7

from api.http.common_exceptions import forbidden, internal_server_error, not_found
from api.http.middleware import IdentityContextFactory, auth_only
from api.http.response_models import DataResponse, ErrorResponse
from core.config import get_settings
from core.dependencies import permission_srv
from domain.entities import Permission
from domain.enums import Action
from domain.errors import ForbiddenError, NotFoundError


settings = get_settings()


if TYPE_CHECKING:
    from domain.dto import IdentityContext
    from services import PermissionService


logger = logging.getLogger(__name__)

router = APIRouter(
    prefix="/permissions",
    tags=["Permissions"],
    dependencies=[Depends(auth_only)],
    responses={
        status.HTTP_401_UNAUTHORIZED: {"model": ErrorResponse},
        status.HTTP_403_FORBIDDEN: {"model": ErrorResponse},
        status.HTTP_500_INTERNAL_SERVER_ERROR: {"model": ErrorResponse},
    },
)

business_element_name = "admin"


@router.get(
    "/{permission_id}",
    summary="Get permission",
    response_model=DataResponse[Permission],
    responses={
        status.HTTP_200_OK: {"description": "Success"},
        status.HTTP_404_NOT_FOUND: {"model": ErrorResponse},
    },
)
async def get_one(
    permission_id: UUID7,
    permission_srv: PermissionService = Depends(permission_srv),
    identity_ctx: IdentityContext = Depends(
        IdentityContextFactory(business_element_name, Action.READ)
    ),
):
    try:
        permission = await permission_srv.get_one(permission_id, identity_ctx)
        return JSONResponse({"data": permission.model_dump(mode="json")})

    except NotFoundError:
        raise not_found("Permission not found")
    except ForbiddenError:
        raise forbidden()
    except Exception as e:
        logger.exception("Error during getting permission: %s", str(e))
        raise internal_server_error()


@router.get(
    "/",
    summary="Get permissions",
    response_model=DataResponse[list[Permission]],
    responses={status.HTTP_200_OK: {"description": "Success"}},
)
async def get_all(
    permission_srv: PermissionService = Depends(permission_srv),
    identity_ctx: IdentityContext = Depends(
        IdentityContextFactory(business_element_name, Action.READ)
    ),
):
    try:
        permissions = await permission_srv.get_all(identity_ctx)
        permissions_response = [p.model_dump(mode="json") for p in permissions]

        return JSONResponse({"data": permissions_response})

    except ForbiddenError:
        raise forbidden()
    except Exception as e:
        logger.exception("Error during getting permissions: %s", str(e))
        raise internal_server_error()
