from __future__ import annotations

import logging
from typing import TYPE_CHECKING

from fastapi import APIRouter, Depends, Response, status
from fastapi.responses import JSONResponse
from pydantic import UUID7

from api.http.common_exceptions import forbidden, internal_server_error, not_found
from api.http.dto import ConfessionCreateDTO, ConfessionUpdateDTO
from api.http.middleware import IdentityContextFactory, auth_only
from api.http.response_models import DataResponse, ErrorResponse, MessageResponse
from core.config import get_settings
from core.dependencies import confession_srv  # Зависимость для сервиса
from domain.entities import Confession
from domain.enums import Action
from domain.errors import ForbiddenError, NotFoundError


settings = get_settings()

if TYPE_CHECKING:
    from domain.dto import IdentityContext
    from services import ConfessionService


logger = logging.getLogger(__name__)

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

business_element_name = "confessions"


@router.post(
    "/",
    summary="Create confession",
    response_model=DataResponse[Confession],
    responses={status.HTTP_201_CREATED: {"description": "Success"}},
)
async def create(
    data: ConfessionCreateDTO,
    confession_srv: ConfessionService = Depends(confession_srv),
    identity_ctx: IdentityContext = Depends(
        IdentityContextFactory(business_element_name, Action.CREATE)
    ),
):
    try:
        confession = await confession_srv.create(data, identity_ctx)
        return JSONResponse(
            {"data": confession.model_dump(mode="json")},
            status_code=status.HTTP_201_CREATED,
        )

    except ForbiddenError:
        raise forbidden()
    except Exception as e:
        logger.exception("Error during creating confession: %s", str(e))
        raise internal_server_error()


@router.get(
    "/{confession_id}",
    summary="Get confession",
    response_model=DataResponse[Confession],
    responses={status.HTTP_200_OK: {"description": "Success"}},
)
async def get_one(
    confession_id: UUID7,
    confession_srv: ConfessionService = Depends(confession_srv),
    identity_ctx: IdentityContext = Depends(
        IdentityContextFactory(business_element_name, Action.READ)
    ),
):
    try:
        confession = await confession_srv.get_one(confession_id, identity_ctx)
        return JSONResponse({"data": confession.model_dump(mode="json")})

    except NotFoundError:
        raise not_found("Confession not found")
    except ForbiddenError:
        raise forbidden()
    except Exception as e:
        logger.exception("Error during getting confession: %s", str(e))
        raise internal_server_error()


@router.get(
    "/",
    summary="Get all confessions",
    response_model=DataResponse[list[Confession]],
    responses={status.HTTP_200_OK: {"description": "Success"}},
)
async def get_all(
    confession_srv: ConfessionService = Depends(confession_srv),
    identity_ctx: IdentityContext = Depends(
        IdentityContextFactory(business_element_name, Action.READ)
    ),
):
    try:
        confessions = await confession_srv.get_all(identity_ctx)
        data = [c.model_dump(mode="json") for c in confessions]
        return JSONResponse({"data": data})

    except ForbiddenError:
        raise forbidden()
    except Exception as e:
        logger.exception("Error during fetching confessions: %s", str(e))
        raise internal_server_error()


@router.patch(
    "/{confession_id}",
    summary="Update confession",
    response_model=DataResponse[Confession],
    responses={status.HTTP_200_OK: {"description": "Success"}},
)
async def update(
    confession_id: UUID7,
    update_data: ConfessionUpdateDTO,
    confession_srv: ConfessionService = Depends(confession_srv),
    identity_ctx: IdentityContext = Depends(
        IdentityContextFactory(business_element_name, Action.UPDATE)
    ),
):
    try:
        confession = await confession_srv.update(confession_id, update_data, identity_ctx)
        return JSONResponse({"data": confession.model_dump(mode="json")})

    except NotFoundError:
        raise not_found("Confession not found")
    except ForbiddenError:
        raise forbidden()
    except Exception as e:
        logger.exception("Error during patching confession: %s", str(e))
        raise internal_server_error()


@router.delete(
    "/{confession_id}",
    summary="Delete confession",
    response_model=MessageResponse,
    responses={status.HTTP_204_NO_CONTENT: {"description": "Success"}},
)
async def delete(
    confession_id: UUID7,
    confession_srv: ConfessionService = Depends(confession_srv),
    identity_ctx: IdentityContext = Depends(
        IdentityContextFactory(business_element_name, Action.DELETE)
    ),
):
    try:
        await confession_srv.delete(confession_id, identity_ctx)
        return Response(status_code=status.HTTP_204_NO_CONTENT)

    except ForbiddenError:
        raise forbidden()
    except Exception as e:
        logger.exception("Error during deleting confession: %s", str(e))
        raise internal_server_error()
