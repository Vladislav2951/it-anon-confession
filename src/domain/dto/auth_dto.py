from typing import Optional

from pydantic import BaseModel, EmailStr, SecretStr

from domain.validators import BioString, NameStr, NicknameStr, PasswordStr


class LoginInput(BaseModel):
    email: EmailStr
    password: SecretStr


class RegisterInput(BaseModel):
    email: EmailStr
    password: PasswordStr
    nickname: NicknameStr
    bio: Optional[BioString]
