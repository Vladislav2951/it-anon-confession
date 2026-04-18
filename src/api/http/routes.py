from fastapi import APIRouter

from api.http.endpoints import auth_router


routers = APIRouter()
_router_list = [auth_router]

for router in _router_list:
    routers.include_router(router)
