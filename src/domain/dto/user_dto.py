from typing import Optional

from pydantic import UUID7, BaseModel, EmailStr, Field, SecretStr

from domain.validators import NameStr


class UserPublic(BaseModel):
    id: UUID7
    email: EmailStr
    first_name: NameStr
    last_name: NameStr
    father_name: Optional[NameStr] = None


class PatchUpdateUserInput(BaseModel):
    email: EmailStr = Field(default=None)  # type: ignore[assignment]
    first_name: NameStr = Field(default=None)  # type: ignore[assignment]
    last_name: NameStr = Field(default=None)  # type: ignore[assignment]

    father_name: Optional[NameStr] = None


class ChangePasswordUserInput(BaseModel):
    password_hash: SecretStr
