from fastapi import APIRouter

from .users import router as admin_users


router = APIRouter(prefix="/admin", tags=["Admin"])

_router_list = [admin_users]

for r in _router_list:
    router.include_router(r)
