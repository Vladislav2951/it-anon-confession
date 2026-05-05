from __future__ import annotations

from datetime import timedelta
import logging
import secrets
from typing import TYPE_CHECKING, Literal

from fastapi import APIRouter, Depends, HTTPException, Request, status
from fastapi.responses import JSONResponse

from api.http.common_exceptions import conflict, internal_server_error, unauthorized
from api.http.dto import LoginDTO, RegisterDTO
from api.http.middleware import auth_only, guest_only
from api.http.response_models import ErrorResponse, MessageResponse
from core.config import get_settings
from core.dependencies import auth_srv, session_srv
from domain.entities import Session
from domain.errors import AppErrorCode, BadLoginError, ConflictError


if TYPE_CHECKING:
    from services import AuthService, SessionService

settings = get_settings()

logger = logging.getLogger(__name__)

router = APIRouter(
    prefix="/auth",
    tags=["Auth"],
    responses={
        status.HTTP_401_UNAUTHORIZED: {"model": ErrorResponse},
        status.HTTP_403_FORBIDDEN: {"model": ErrorResponse},
        status.HTTP_422_UNPROCESSABLE_CONTENT: {"description": "Validation error"},
        status.HTTP_500_INTERNAL_SERVER_ERROR: {"model": ErrorResponse},
    },
)

httponly = True
secure = True
samesite: Literal["lax", "strict", "none"] | None = "lax"
if settings.ENV == "dev":
    secure = False
if settings.ENV == "test":
    secure = False
    httponly = False


@router.post(
    "/login",
    dependencies=[Depends(guest_only)],
    summary="Login",
    response_model=MessageResponse,
    responses={status.HTTP_200_OK: {"description": "Success"}},
)
async def login(
    request: Request,
    credentials: LoginDTO,
    auth_srv: AuthService = Depends(auth_srv),
    session_srv: SessionService = Depends(session_srv),
):
    try:
        user = await auth_srv.login(credentials)

        user_agent = request.headers.get("user-agent")
        ip_address = request.client.host if request.client else None

        expires_in_seconds = int(
            timedelta(days=settings.SESSION_DURATION_DAYS).total_seconds()
        )
        token = secrets.token_urlsafe(64)

        session = Session.create(
            token=token,
            user_id=user.id,
            expires_in_seconds=expires_in_seconds,
            user_agent=user_agent,
            ip_address=ip_address,
        )
        await session_srv.save(session)

        response = JSONResponse(
            content={"message": "Success!"}, status_code=status.HTTP_200_OK
        )
        response.set_cookie(
            key="session_id",
            value=token,
            httponly=httponly,
            secure=secure,
            samesite=samesite,
            max_age=expires_in_seconds,
        )

        return response

    except BadLoginError:
        raise unauthorized("Incorrect email or password")
    except Exception:
        logger.exception("Unexpected error while logging %s user", credentials.email)
        raise internal_server_error()


@router.post(
    "/logout",
    dependencies=[Depends(auth_only)],
    summary="Logout",
    response_model=MessageResponse,
    responses={status.HTTP_200_OK: {"description": "Success"}},
)
async def logout(request: Request, session_srv: SessionService = Depends(session_srv)):
    session_id = request.cookies.get("session_id")
    if not session_id:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail={
                "code": AppErrorCode.INTERNAL_SERVER_ERROR,
                "message": "Logout failed",
            },
        )

    try:
        await session_srv.delete(session_id)

        response = JSONResponse({"message": "Successfully logged out"})
        response.delete_cookie(key="session_id")
        return response

    except Exception as e:
        logger.exception("Error during logout: %s", str(e))
        raise internal_server_error()


@router.post(
    "/register",
    dependencies=[Depends(guest_only)],
    summary="Register",
    description="Register new user",
    response_model=MessageResponse,
    responses={
        status.HTTP_201_CREATED: {"description": "User has been registered"},
        status.HTTP_409_CONFLICT: {
            "description": "User already exists",
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
        raise conflict("User already exists")
    except Exception:
        logger.exception("Unexpected error while registering %s user", data.email)
        raise internal_server_error()
