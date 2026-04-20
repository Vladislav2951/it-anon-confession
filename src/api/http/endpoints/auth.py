from __future__ import annotations

from datetime import timedelta
import logging
import secrets
from typing import TYPE_CHECKING, Literal

from fastapi import APIRouter, Depends, HTTPException, Request, status
from fastapi.responses import JSONResponse

from api.http.dto import LoginDTO, RegisterDTO
from api.http.middleware import auth_only, guest_only
from api.http.response_models import ErrorResponse, MessageResponse
from core.config import get_settings
from core.dependencies import auth_srv, session_srv
from domain.entities import Session
from domain.errors import AppErrorCode, BadLoginError, ConflictError


settings = get_settings()


if TYPE_CHECKING:
    from services import AuthService, SessionService


logger = logging.getLogger(__name__)

router = APIRouter(prefix="/auth", tags=["Auth"])

secure = False
samesite: Literal["lax", "strict", "none"] | None = "lax"
if settings.ENV == "prod":
    secure = True
    samesite = "lax"


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
            httponly=True,
            secure=secure,
            samesite=samesite,
            max_age=expires_in_seconds,
        )

        return response
    except BadLoginError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, detail="Incorrect email or password"
        )
    except Exception:
        logger.exception("Unexpected error while logging %s user", credentials.email)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail={
                "code": AppErrorCode.INTERNAL_SERVER_ERROR,
                "message": "An unexpected error occurred",
            },
        )


@router.post(
    "/logout",
    dependencies=[Depends(auth_only)],
    summary="Logout",
    response_model=MessageResponse,
    responses={
        status.HTTP_200_OK: {"description": "Success"},
        status.HTTP_401_UNAUTHORIZED: {"model": ErrorResponse},
        status.HTTP_403_FORBIDDEN: {"model": ErrorResponse},
        status.HTTP_500_INTERNAL_SERVER_ERROR: {"model": ErrorResponse},
    },
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
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail={
                "code": AppErrorCode.INTERNAL_SERVER_ERROR,
                "message": "An unexpected error occurred",
            },
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
                "message": "An unexpected error occurred",
            },
        )
