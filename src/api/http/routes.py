from fastapi import APIRouter

from api.http.endpoints import admin_router, auth_router, user_router


routers = APIRouter()
_router_list = [auth_router, user_router, admin_router]

for router in _router_list:
    routers.include_router(router)
