from fastapi import HTTPException, status
from starlette.requests import Request

from domain.errors import AppErrorCode


async def guest_only(request: Request):
    if request.cookies.get("session_id"):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail={
                "code": AppErrorCode.FORBIDDEN,
                "message": "For unregistered users only",
            },
        )

    return
