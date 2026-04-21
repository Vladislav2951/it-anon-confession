from __future__ import annotations

from typing import TYPE_CHECKING

from fastapi import Depends

from domain.dto import IdentityContext

from .get_current_user_mw import get_current_user


if TYPE_CHECKING:
    from domain.entities import User
    from domain.enums import Action


class IdentityContextFactory:
    def __init__(self, business_element_name: str, action: Action):
        self.business_element_name = business_element_name
        self.action = action

    async def __call__(
        self, current_user: User = Depends(get_current_user)
    ) -> IdentityContext:
        return IdentityContext(
            current_user=current_user,
            business_element_name=self.business_element_name,
            action=self.action,
        )
