from typing import Optional

from pydantic import BaseModel, EmailStr, Field, SecretStr

from domain.validators import BioString, NicknameStr


class PatchUpdateUserInput(BaseModel):
    email: EmailStr = Field(default=None)  # type: ignore[assignment]
    nickname: NicknameStr = Field(default=None)  # type: ignore[assignment]

    bio: Optional[BioString] = None


class ChangePasswordUserInput(BaseModel):
    password_hash: SecretStr
