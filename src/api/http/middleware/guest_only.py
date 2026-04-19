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


# async def guest_only(
#     token_creds: HTTPAuthorizationCredentials | None = Depends(
#         HTTPBearer(auto_error=False)
#     ),
# ):
#     if token_creds is None:
#         return

#     try:
#         token = token_creds.credentials
#         decode_jwt(token)

#         # Если decode_jwt не выбросил исключение, значит пользователь авторизован.
#         # Для guest_only это запрещенное состояние.
#         raise HTTPException(
#             status_code=status.HTTP_403_FORBIDDEN,
#             detail={
#                 "code": AppErrorCode.FORBIDDEN,
#                 "message": "You are already logged in",
#             },
#         )
#     except InvalidTokenError:
#         # Если токен "битый" или просрочен - считаем пользователя гостем
#         return
