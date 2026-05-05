from __future__ import annotations

import logging
from typing import TYPE_CHECKING, Optional

from fastapi import Depends, Path, Request
from pydantic import UUID7

from api.http.common_exceptions import forbidden, internal_server_error
from api.http.middleware.get_current_user_mw import get_current_user
from core.dependencies import access_srv, confession_srv, user_srv
from domain.errors import ForbiddenError
from domain.validators import Identifier


if TYPE_CHECKING:
    from domain.entities import User
    from domain.enums import Action
    from services import AccessService, ConfessionService, UserService


logger = logging.getLogger(__name__)


class PermissionChecker:
    def __init__(self, business_element_name: str, action: Action):
        self.business_element_name = business_element_name
        self.action = action

    async def __call__(
        self,
        access_srv: AccessService = Depends(access_srv),
        current_user: User = Depends(get_current_user),
    ):
        try:
            await access_srv.check_access(
                current_user, self.business_element_name, self.action
            )
        except ForbiddenError:
            raise forbidden()


async def get_confession_id(request: Request) -> Optional[UUID7]:
    confession_id = request.path_params.get("confession_id")
    if not confession_id:
        return None

    try:
        return UUID7(confession_id)
    except Exception as e:
        logger.error("confession_id=%s from parameters is not UUID: %s", confession_id, e)
        raise internal_server_error()


class ConfessionPermissionChecker:
    def __init__(self, business_element_name: str, action: Action):
        self.business_element_name = business_element_name
        self.action = action

    async def __call__(
        self,
        access_srv: AccessService = Depends(access_srv),
        confession_srv: ConfessionService = Depends(confession_srv),
        current_user: User = Depends(get_current_user),
        confession_id: UUID7 = Depends(get_confession_id),
    ):
        try:
            owner_id = await confession_srv.get_owner_id(confession_id)
            await access_srv.check_access(
                current_user, self.business_element_name, self.action, owner_id
            )
        except ForbiddenError:
            raise forbidden()
        except Exception as e:
            logger.error(
                "Unexpected error while getting confession (id=%s) owner: %s",
                confession_id,
                e,
            )
            raise internal_server_error()


async def get_user_identifier(identifier: Identifier = Path()) -> Identifier:
    return identifier
    # if not identifier:
    #     return None

    # try:
    #     return UUID7(identifier)
    # except Exception:
    #     if isinstance(identifier, str):
    #         return identifier

    # logger.error(
    #     "identifier=%s (type: %s) from parameters is not UUID or str",
    #     identifier,
    #     type(identifier),
    # )
    # raise internal_server_error()


class UserPermissionChecker:
    def __init__(self, business_element_name: str, action: Action):
        self.business_element_name = business_element_name
        self.action = action

    async def __call__(
        self,
        access_srv: AccessService = Depends(access_srv),
        user_srv: UserService = Depends(user_srv),
        current_user: User = Depends(get_current_user),
        user_identifier: Identifier = Depends(get_user_identifier),
    ):
        try:
            owner_id = await user_srv.get_owner_id(user_identifier)
            await access_srv.check_access(
                current_user, self.business_element_name, self.action, owner_id
            )
        except ForbiddenError:
            raise forbidden()
        except Exception as e:
            logger.error(
                "Unexpected error while getting user (identifier=%s) owner: %s",
                user_identifier,
                e,
            )
            raise internal_server_error()
