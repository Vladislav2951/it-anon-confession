from datetime import datetime, timedelta, timezone
from logging import getLogger
from typing import Any, Literal, Optional

import bcrypt
import jwt
from pydantic import BaseModel

from core.config import get_settings


logger = getLogger(__name__)

settings = get_settings()

ALGORITHM = "HS256"


class TokenInfo(BaseModel):
    access_token: str
    token_type: Literal["Bearer"]


def create_access_token(payload: dict[str, Any]) -> str:
    to_encode = payload.copy()
    now = datetime.now(timezone.utc)
    expire = now + timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)

    to_encode.update({"exp": expire, "iat": now})
    return jwt.encode(
        to_encode, settings.JWT_SECRET.get_secret_value(), algorithm=ALGORITHM
    )


def verify_password(plain_password: str, hashed_password: str) -> bool:
    return bcrypt.checkpw(plain_password.encode(), hashed_password.encode())


def get_password_hash(password: str) -> str:
    return bcrypt.hashpw(password.encode(), bcrypt.gensalt()).decode()


def decode_jwt(token: str) -> dict[str, Any]:
    return jwt.decode(
        token, settings.JWT_SECRET.get_secret_value(), algorithms=[ALGORITHM]
    )


# def validate_jwt(token: str) -> bool:
#     try:
#         # Check if the token has expired
#         if decoded_token.get("exp", 0) > datetime.now(timezone.utc).timestamp():
#             return decoded_token
#         return None
#     except jwt.PyJWTError as e:
#         logger.debug("Decode JWT error: %s", e)
#         return None  # Catches ExpiredSignatureError, InvalidTokenError etc.
#     return False
