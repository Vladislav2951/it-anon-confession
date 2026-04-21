from fastapi import HTTPException, status

from domain.errors import AppErrorCode


unauthorized = HTTPException(
    status_code=status.HTTP_401_UNAUTHORIZED,
    detail={"code": AppErrorCode.UNAUTHORIZED, "message": "Invalid or expired session"},
)

forbidden = HTTPException(
    status_code=status.HTTP_403_FORBIDDEN,
    detail={"code": AppErrorCode.FORBIDDEN, "message": "Access denied"},
)

not_found = HTTPException(
    status_code=status.HTTP_404_NOT_FOUND,
    detail={"code": AppErrorCode.NOT_FOUND, "message": "Resource not found"},
)

internal_server_error = HTTPException(
    status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
    detail={
        "code": AppErrorCode.INTERNAL_SERVER_ERROR,
        "message": "An unexpected error occurred",
    },
)
