from enum import Enum
from typing import Optional


class AppErrorCode(str, Enum):
    BAD_REQUEST = "BAD_REQUEST"
    BAD_LOGIN = "BAD_LOGIN"
    CONFLICT = "CONFLICT"
    INTERNAL_SERVER_ERROR = "INTERNAL_SERVER_ERROR"
    FORBIDDEN = "FORBIDDEN"
    NOT_FOUND = "NOT_FOUND"
    UNAUTHORIZED = "UNAUTHORIZED"
    UNPROCESSABLE = "UNPROCESSABLE"


class AppError(Exception):
    def __init__(self, message: Optional[str], code: AppErrorCode):
        super().__init__(message)
        self.message = message
        self.code = code


class ForbiddenError(AppError):
    def __init__(self, message: Optional[str] = None):
        super().__init__(message, code=AppErrorCode.FORBIDDEN)


class UnauthorizedError(AppError):
    def __init__(self, message: Optional[str] = None):
        super().__init__(message, code=AppErrorCode.UNAUTHORIZED)


class NotFoundError(AppError):
    def __init__(self, message: Optional[str] = None):
        super().__init__(message, code=AppErrorCode.NOT_FOUND)


class BadLoginError(AppError):
    def __init__(self, message: Optional[str] = None):
        super().__init__(message, code=AppErrorCode.BAD_LOGIN)


class ConflictError(AppError):
    def __init__(self, message: Optional[str] = None):
        super().__init__(message, code=AppErrorCode.CONFLICT)


class UpdateError(AppError):
    def __init__(self, message: Optional[str] = None):
        super().__init__(message, code=AppErrorCode.BAD_REQUEST)


class Unprocessable(AppError):
    def __init__(self, message: Optional[str] = None):
        super().__init__(message, code=AppErrorCode.BAD_REQUEST)
