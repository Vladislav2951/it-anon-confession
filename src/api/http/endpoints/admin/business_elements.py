from __future__ import annotations

import logging
from typing import TYPE_CHECKING, Annotated

from fastapi import APIRouter, Depends, Query, status
from fastapi.responses import JSONResponse
from pydantic import UUID7

from api.http.common_exceptions import forbidden, internal_server_error, not_found
from api.http.dto import PaginationDTO
from api.http.middleware import IdentityContextFactory, auth_only
from api.http.response_models import DataManyResponse, DataResponse, ErrorResponse, Meta
from core.config import get_settings
from core.dependencies import business_element_srv
from domain.entities import BusinessElement
from domain.enums import Action
from domain.errors import ForbiddenError, NotFoundError


settings = get_settings()

if TYPE_CHECKING:
    from domain.dto import IdentityContext
    from services import BusinessElementService


logger = logging.getLogger(__name__)

router = APIRouter(
    prefix="/business-elements",
    tags=["Business Elements"],
    dependencies=[Depends(auth_only)],
    responses={
        status.HTTP_401_UNAUTHORIZED: {"model": ErrorResponse},
        status.HTTP_403_FORBIDDEN: {"model": ErrorResponse},
        status.HTTP_500_INTERNAL_SERVER_ERROR: {"model": ErrorResponse},
    },
)

business_element_name = "admin"


@router.get(
    "/{element_id}",
    summary="Get business element",
    response_model=DataResponse[BusinessElement],
    responses={
        status.HTTP_200_OK: {"description": "Success"},
        status.HTTP_404_NOT_FOUND: {"model": ErrorResponse},
    },
)
async def get_one(
    element_id: UUID7,
    be_srv: BusinessElementService = Depends(business_element_srv),
    identity_ctx: IdentityContext = Depends(
        IdentityContextFactory(business_element_name, Action.READ)
    ),
):
    try:
        element = await be_srv.get_one(element_id, identity_ctx)
        return JSONResponse({"data": element.model_dump(mode="json")})

    except NotFoundError:
        raise not_found("Business element not found")
    except ForbiddenError:
        raise forbidden()
    except Exception as e:
        logger.exception("Error during getting business element: %s", str(e))
        raise internal_server_error()


@router.get(
    "/",
    summary="Get all business elements",
    response_model=DataManyResponse[BusinessElement],
    responses={status.HTTP_200_OK: {"description": "Success"}},
)
async def get_all(
    pagination: Annotated[PaginationDTO, Query()],
    be_srv: BusinessElementService = Depends(business_element_srv),
    identity_ctx: IdentityContext = Depends(
        IdentityContextFactory(business_element_name, Action.READ)
    ),
):
    try:
        elements, total = await be_srv.get_all(
            identity_ctx, pagination.limit, pagination.offset
        )

        data = [el.model_dump(mode="json") for el in elements]
        meta = Meta(page=pagination.page, size=pagination.size, total_items=total)

        return {"data": data, "meta": meta}

    except ForbiddenError:
        raise forbidden()
    except Exception as e:
        logger.exception("Error during fetching business elements: %s", str(e))
        raise internal_server_error()
