from __future__ import annotations

import logging
from typing import TYPE_CHECKING, Annotated

from fastapi import APIRouter, Depends, Query, Response, status
from fastapi.responses import JSONResponse
from pydantic import UUID7

from api.http.common_exceptions import internal_server_error, not_found
from api.http.dto import (
    ConfessionCreateDTO,
    ConfessionPublic,
    ConfessionUpdateDTO,
    PaginationDTO,
)
from api.http.middleware import (
    ConfessionPermissionChecker,
    PermissionChecker,
    auth_only,
    get_current_user,
)
from api.http.response_models import DataManyResponse, DataResponse, ErrorResponse, Meta
from core.config import get_settings
from core.dependencies import confession_srv
from domain.enums import Action
from domain.errors import NotFoundError


if TYPE_CHECKING:
    from domain.entities import User
    from services import ConfessionService

settings = get_settings()

logger = logging.getLogger(__name__)

business_element_name = "confessions"

router = APIRouter(
    prefix="/confessions",
    tags=["Confessions"],
    dependencies=[Depends(auth_only)],
    responses={
        status.HTTP_401_UNAUTHORIZED: {"model": ErrorResponse},
        status.HTTP_403_FORBIDDEN: {"model": ErrorResponse},
        status.HTTP_500_INTERNAL_SERVER_ERROR: {"model": ErrorResponse},
    },
)


@router.post(
    "/",
    summary="Create confession",
    response_model=DataResponse[ConfessionPublic],
    responses={status.HTTP_201_CREATED: {"description": "Success"}},
    dependencies=[Depends(PermissionChecker(business_element_name, Action.CREATE))],
)
async def create(
    data: ConfessionCreateDTO,
    confession_srv: ConfessionService = Depends(confession_srv),
    current_user: User = Depends(get_current_user),
):
    try:
        confession = await confession_srv.create(data, current_user)
        return JSONResponse(
            {
                "data": ConfessionPublic.model_validate(
                    confession, from_attributes=True
                ).model_dump(mode="json")
            },
            status_code=status.HTTP_201_CREATED,
        )

    except Exception as e:
        logger.exception("Error during creating confession: %s", str(e))
        raise internal_server_error()


@router.get(
    "/{confession_id}",
    summary="Get confession",
    response_model=DataResponse[ConfessionPublic],
    responses={status.HTTP_200_OK: {"description": "Success"}},
    dependencies=[Depends(PermissionChecker(business_element_name, Action.READ))],
)
async def get_one(
    confession_id: UUID7, confession_srv: ConfessionService = Depends(confession_srv)
):
    try:
        confession = await confession_srv.get_one(confession_id)
        return JSONResponse(
            {
                "data": ConfessionPublic.model_validate(
                    confession, from_attributes=True
                ).model_dump(mode="json")
            }
        )

    except NotFoundError:
        raise not_found("Confession not found")
    except Exception as e:
        logger.exception("Error during getting confession: %s", str(e))
        raise internal_server_error()


@router.get(
    "/",
    summary="Get all confessions",
    response_model=DataManyResponse[ConfessionPublic],
    responses={status.HTTP_200_OK: {"description": "Success"}},
    dependencies=[Depends(PermissionChecker(business_element_name, Action.READ))],
)
async def get_all(
    pagination: Annotated[PaginationDTO, Query()],
    confession_srv: ConfessionService = Depends(confession_srv),
):
    try:
        confessions, total = await confession_srv.get_all(
            pagination.limit, pagination.offset
        )

        data = [
            ConfessionPublic.model_validate(c, from_attributes=True).model_dump(
                mode="json"
            )
            for c in confessions
        ]
        meta = Meta(page=pagination.page, size=pagination.size, total_items=total)

        return {"data": data, "meta": meta}

    except Exception as e:
        logger.exception("Error during fetching confessions: %s", str(e))
        raise internal_server_error()


@router.patch(
    "/{confession_id}",
    summary="Update confession",
    response_model=DataResponse[ConfessionPublic],
    responses={status.HTTP_200_OK: {"description": "Success"}},
    dependencies=[
        Depends(ConfessionPermissionChecker(business_element_name, Action.UPDATE))
    ],
)
async def update(
    confession_id: UUID7,
    update_data: ConfessionUpdateDTO,
    confession_srv: ConfessionService = Depends(confession_srv),
):
    try:
        confession = await confession_srv.update(confession_id, update_data)
        return JSONResponse(
            {
                "data": ConfessionPublic.model_validate(
                    confession, from_attributes=True
                ).model_dump(mode="json")
            }
        )

    except NotFoundError:
        raise not_found("Confession not found")
    except Exception as e:
        logger.exception("Error during patching confession: %s", str(e))
        raise internal_server_error()


@router.delete(
    "/{confession_id}",
    summary="Delete confession",
    responses={status.HTTP_204_NO_CONTENT: {"description": "Success"}},
    dependencies=[
        Depends(ConfessionPermissionChecker(business_element_name, Action.DELETE))
    ],
)
async def delete(
    confession_id: UUID7, confession_srv: ConfessionService = Depends(confession_srv)
):
    try:
        await confession_srv.delete(confession_id)
        return Response(status_code=status.HTTP_204_NO_CONTENT)

    except Exception as e:
        logger.exception("Error during deleting confession: %s", str(e))
        raise internal_server_error()
