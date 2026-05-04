from fastapi import HTTPException, status

from domain.errors import AppErrorCode


def unauthorized(message: str = "Invalid or expired session") -> HTTPException:
    return HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail={"code": AppErrorCode.UNAUTHORIZED, "message": message},
    )


def forbidden(message: str = "Access denied") -> HTTPException:
    return HTTPException(
        status_code=status.HTTP_403_FORBIDDEN,
        detail={"code": AppErrorCode.FORBIDDEN, "message": message},
    )


def not_found(message: str = "Resource not found") -> HTTPException:
    return HTTPException(
        status_code=status.HTTP_404_NOT_FOUND,
        detail={"code": AppErrorCode.NOT_FOUND, "message": message},
    )


def conflict(message: str = "Resource already exists") -> HTTPException:
    return HTTPException(
        status_code=status.HTTP_409_CONFLICT,
        detail={"code": AppErrorCode.CONFLICT, "message": message},
    )


def unprocessable(message: str = "Business validation error") -> HTTPException:
    return HTTPException(
        status_code=status.HTTP_422_UNPROCESSABLE_CONTENT,
        detail={"code": AppErrorCode.UNPROCESSABLE, "message": message},
    )


def internal_server_error(message: str = "An unexpected error occurred") -> HTTPException:
    return HTTPException(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        detail={"code": AppErrorCode.INTERNAL_SERVER_ERROR, "message": message},
    )
