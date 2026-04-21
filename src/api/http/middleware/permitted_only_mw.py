from __future__ import annotations

from typing import TYPE_CHECKING

from fastapi import Depends, HTTPException, status

from core.dependencies import user_srv
from domain.validators import PermissionSlug

from .get_current_user_mw import get_current_user


if TYPE_CHECKING:
    from domain.entities import User
    from services import UserService


class PermissionRequired:
    def __init__(self, *required_permissions: PermissionSlug):
        self.required_permissions = required_permissions

    async def __call__(
        self,
        current_user: User = Depends(get_current_user),
        user_srv: UserService = Depends(user_srv),
    ):
        # permissions = await user_srv.get_permissions(current_user.id)

        # for perm in self.required_permissions:
        #     if current_user.has_permission(perm):
        #         return True

        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN, detail="Permission denied"
        )
