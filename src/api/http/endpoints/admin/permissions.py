from __future__ import annotations

import logging
from typing import TYPE_CHECKING, Annotated

from fastapi import APIRouter, Depends, Query, status
from fastapi.responses import JSONResponse
from pydantic import UUID7

from api.http.common_exceptions import internal_server_error, not_found
from api.http.dto import PaginationDTO
from api.http.middleware import PermissionChecker
from api.http.response_models import DataManyResponse, DataResponse, ErrorResponse, Meta
from core.config import get_settings
from core.dependencies import permission_srv
from domain.entities import Permission
from domain.enums import Action
from domain.errors import NotFoundError


settings = get_settings()


if TYPE_CHECKING:
    from services import PermissionService


logger = logging.getLogger(__name__)

business_element_name = "admin"

router = APIRouter(
    prefix="/permissions",
    tags=["Permissions"],
    responses={
        status.HTTP_401_UNAUTHORIZED: {"model": ErrorResponse},
        status.HTTP_403_FORBIDDEN: {"model": ErrorResponse},
        status.HTTP_500_INTERNAL_SERVER_ERROR: {"model": ErrorResponse},
    },
)


@router.get(
    "/{permission_id}",
    summary="Get permission",
    response_model=DataResponse[Permission],
    responses={
        status.HTTP_200_OK: {"description": "Success"},
        status.HTTP_404_NOT_FOUND: {"model": ErrorResponse},
    },
    dependencies=[Depends(PermissionChecker(business_element_name, Action.READ))],
)
async def get_one(
    permission_id: UUID7, permission_srv: PermissionService = Depends(permission_srv)
):
    try:
        permission = await permission_srv.get_one(permission_id)
        return JSONResponse({"data": permission.model_dump(mode="json")})

    except NotFoundError:
        raise not_found("Permission not found")
    except Exception as e:
        logger.exception("Error during getting permission: %s", str(e))
        raise internal_server_error()


@router.get(
    "/",
    summary="Get permissions",
    response_model=DataManyResponse[Permission],
    responses={status.HTTP_200_OK: {"description": "Success"}},
    dependencies=[Depends(PermissionChecker(business_element_name, Action.READ))],
)
async def get_all(
    pagination: Annotated[PaginationDTO, Query()],
    permission_srv: PermissionService = Depends(permission_srv),
):
    try:
        permissions, total = await permission_srv.get_all(
            pagination.limit, pagination.offset
        )

        data = [p.model_dump(mode="json") for p in permissions]
        meta = Meta(page=pagination.page, size=pagination.size, total_items=total)

        return {"data": data, "meta": meta}

    except Exception as e:
        logger.exception("Error during getting permissions: %s", str(e))
        raise internal_server_error()
