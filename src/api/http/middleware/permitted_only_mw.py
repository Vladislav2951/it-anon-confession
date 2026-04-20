from __future__ import annotations

from typing import TYPE_CHECKING

from fastapi import Depends, HTTPException, status

from domain.validators import PermissionSlug

from .get_current_user_mw import get_current_user


if TYPE_CHECKING:
    from domain.entities import User


class PermissionRequired:
    def __init__(self, *required_permissions: PermissionSlug):
        self.required_permissions = required_permissions

    async def __call__(self, current_user: User = Depends(get_current_user)):
        # Есть ли хотя бы одно из разрешений
        for perm in self.required_permissions:
            if current_user.has_permission(perm):
                return True

        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN, detail="Permission denied"
        )
