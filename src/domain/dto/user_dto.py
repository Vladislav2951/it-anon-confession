from typing import Optional

from pydantic import UUID7, BaseModel, EmailStr

from domain.validators import NameStr


class UserPublic(BaseModel):
    id: UUID7
    email: EmailStr
    first_name: NameStr
    last_name: NameStr
    father_name: Optional[NameStr] = None
