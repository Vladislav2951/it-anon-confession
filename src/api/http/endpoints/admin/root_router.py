from fastapi import APIRouter

from .permissions import router as admin_permissions
from .roles import router as admin_roles
from .users import router as admin_users


router = APIRouter(prefix="/admin", tags=["Admin"])

_router_list = [admin_users, admin_roles, admin_permissions]

for r in _router_list:
    router.include_router(r)
