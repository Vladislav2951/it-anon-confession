from __future__ import annotations

import logging
from typing import TYPE_CHECKING, Annotated, Literal

from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.responses import JSONResponse

from api.http.dto import LoginDTO, RegisterDTO
from api.http.middleware import guest_only
from api.http.response_models import DataResponse, ErrorResponse, MessageResponse
from core.config import get_settings
from core.dependencies import auth_srv
from core.security import TokenInfo, create_access_token
from domain.errors import AppErrorCode, BadLogin, ConflictError


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


@router.post(
    "/login",
    dependencies=[Depends(guest_only)],
    summary="Login",
    response_model=MessageResponse,
    responses={
        status.HTTP_200_OK: {"description": "Success"},
        status.HTTP_401_UNAUTHORIZED: {
            "description": "Unauthorized",
            "model": ErrorResponse,
        },
        status.HTTP_403_FORBIDDEN: {"description": "Forbidden", "model": ErrorResponse},
        status.HTTP_422_UNPROCESSABLE_CONTENT: {"description": "Validation error"},
        status.HTTP_500_INTERNAL_SERVER_ERROR: {
            "description": "Something went wrong",
            "model": ErrorResponse,
        },
    },
)
async def login(credentials: LoginDTO, srv: AuthService = Depends(auth_srv)):
    try:
        user = await srv.login(credentials)

        jwt_payload = {"sub": str(user.id)}
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


@router.post(
    "/register",
    dependencies=[Depends(guest_only)],
    summary="Register",
    description="Register new user",
    response_model=MessageResponse,
    responses={
        status.HTTP_201_CREATED: {"description": "User has been registered"},
        status.HTTP_401_UNAUTHORIZED: {
            "description": "Unauthorized",
            "model": ErrorResponse,
        },
        status.HTTP_400_BAD_REQUEST: {
            "description": "Incorrect data entered",
            "model": ErrorResponse,
        },
        status.HTTP_409_CONFLICT: {
            "description": "User is already exist",
            "model": ErrorResponse,
        },
        #! fix response model
        status.HTTP_422_UNPROCESSABLE_CONTENT: {"description": "Validation error"},
        status.HTTP_500_INTERNAL_SERVER_ERROR: {
            "description": "Something went wrong",
            "model": ErrorResponse,
        },
    },
)
async def register(data: RegisterDTO, srv: AuthService = Depends(auth_srv)):
    try:
        await srv.register(data)
        return JSONResponse(
            status_code=status.HTTP_201_CREATED,
            content={"message": "User has been registered"},
        )
    except ConflictError:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail={"code": AppErrorCode.CONFLICT, "message": "User is already exist"},
        )

    except Exception:
        logger.exception("Unexpected error while registering %s user", data.email)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail={
                "code": AppErrorCode.INTERNAL_SERVER_ERROR,
                "message": "An unexpected error occurred while registering a user",
            },
        )
