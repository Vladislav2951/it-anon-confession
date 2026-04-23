import hashlib

import bcrypt


def verify_password(plain_password: str, hashed_password: str) -> bool:
    return bcrypt.checkpw(plain_password.encode(), hashed_password.encode())


def get_password_hash(password: str) -> str:
    return bcrypt.hashpw(password.encode(), bcrypt.gensalt()).decode()


def get_token_hash(token: str) -> str:
    return hashlib.sha256(token.encode()).hexdigest()
