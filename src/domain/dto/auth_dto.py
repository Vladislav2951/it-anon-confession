from typing import Optional

from pydantic import BaseModel, EmailStr, SecretStr

from core.validators import NameStr, PasswordStr


class LoginInput(BaseModel):
    email: EmailStr
    password: SecretStr


class RegisterInput(BaseModel):
    email: EmailStr
    password: PasswordStr
    first_name: NameStr
    last_name: NameStr
    father_name: Optional[NameStr]
