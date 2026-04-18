from __future__ import annotations

import logging
from typing import TYPE_CHECKING, Annotated, Literal

from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.responses import JSONResponse

from api.http.endpoints.dto import LoginDTO
from core.config import get_settings
from core.dependencies import auth_srv
from core.security import TokenInfo, create_access_token
from domain.errors import BadLogin


settings = get_settings()


if TYPE_CHECKING:
    from services import AuthService


logger = logging.getLogger(__name__)

router = APIRouter(prefix="/auth", tags=["Auth"])

# secure: bool = False
# samesite: Literal["lax", "strict", "none"] | None = "lax"
# if settings.ENV == "prod":
#     secure = True
#     samesite = "lax"


@router.post("/login")
async def login(credentials: LoginDTO, srv: AuthService = Depends(auth_srv)):
    try:
        user = await srv.login(credentials)

        jwt_payload = {"sub": user.id}
        access_token = create_access_token(jwt_payload)
        token_info = TokenInfo(access_token=access_token, token_type="Bearer")

        # response.set_cookie(
        #     key="access_token",
        #     value=access_token,
        #     httponly=True,          # 🔒 защита от JS (XSS)
        #     secure=True,            # 🔒 только HTTPS (в dev можно False)
        #     samesite="lax",         # защита от CSRF
        #     max_age=60 * 15,        # 15 минут
        # )

        headers = {"Authorization": f"Bearer {access_token}"}
        # TODO передавать токен в теле
        return JSONResponse(
            content={"message": "Success!"},
            status_code=status.HTTP_200_OK,
            headers=headers,
        )
    except BadLogin:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, detail="Incorrect email or password"
        )
