from enum import Enum


class AppErrorCode(str, Enum):
    BAD_LOGIN = "BAD_LOGIN"


class AppError(Exception):
    def __init__(self, message: str, code: AppErrorCode):
        super().__init__(message)
        self.message = message
        self.code = code


# class ForbiddenError(AppError):
#     def __init__(self, message="Forbidden action"):
#         super().__init__(message, code=403)


class BadLogin(AppError):
    def __init__(self, message):
        super().__init__(message, code=AppErrorCode.BAD_LOGIN)
