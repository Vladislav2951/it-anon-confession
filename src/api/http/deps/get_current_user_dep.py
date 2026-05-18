from fastapi import HTTPException, Request, status

from domain.entities import User
from domain.errors import AppErrorCode


def get_current_user(request: Request) -> User:
    user = request.state.user
    if not (user and isinstance(user, User)):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail={
                "code": AppErrorCode.UNAUTHORIZED,
                "message": "Invalid or expired session",
            },
        )

    return user
