from __future__ import annotations

from typing import TYPE_CHECKING

from fastapi import Depends

from api.http.common_exceptions import forbidden
from api.http.middleware import get_current_user
from core.dependencies import access_srv
from domain.errors import ForbiddenError


if TYPE_CHECKING:
    from domain.entities import User
    from domain.enums import Action
    from services import AccessService


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
