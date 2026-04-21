from __future__ import annotations

from typing import TYPE_CHECKING, Optional

from fastapi import Depends, HTTPException, Request, status

from core.dependencies import access_srv
from domain.errors import ForbiddenError, UnauthorizedError

from .get_current_user_mw import get_current_user


if TYPE_CHECKING:
    from pydantic import UUID7

    from domain.entities import User
    from domain.enums import Action
    from services import AccessService


class AccessRequired:
    def __init__(
        self, business_element_name: str, action: Action, owner_id: Optional[UUID7] = None
    ):
        self.business_element_name = business_element_name
        self.action = action
        self.owner_id = owner_id

    async def __call__(
        self,
        current_user: User = Depends(get_current_user),
        access_srv: AccessService = Depends(access_srv),
    ):
        try:
            await access_srv.check_access(
                current_user, self.business_element_name, self.action, self.owner_id
            )
        except (ForbiddenError, UnauthorizedError):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN, detail="Permission denied"
            )
