from .admin import admin_router
from .auth import router as auth_router
from .users import router as user_router


__all__ = ["auth_router", "admin_router", "user_router"]
