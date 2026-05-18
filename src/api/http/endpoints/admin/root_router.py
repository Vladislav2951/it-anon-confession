from fastapi import APIRouter, Depends

from api.http.deps import auth_only

from .business_elements import router as admin_business_elements
from .permissions import router as admin_permissions
from .roles import router as admin_roles
from .users import router as admin_users


router = APIRouter(prefix="/admin", tags=["Admin"], dependencies=[Depends(auth_only)])

_router_list = [admin_users, admin_roles, admin_permissions, admin_business_elements]

for r in _router_list:
    router.include_router(r)
