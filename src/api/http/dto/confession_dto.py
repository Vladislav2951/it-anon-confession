from datetime import datetime

from pydantic import UUID7, BaseModel

from domain.dto import ConfessionCreateInput, ConfessionUpdateInput
from domain.validators import BodyString, NicknameStr, TitleStr


class ConfessionCreateDTO(ConfessionCreateInput):
    pass


class ConfessionUpdateDTO(ConfessionUpdateInput):
    pass


class ConfessionPublic(BaseModel):
    id: UUID7
    title: TitleStr
    body: BodyString
    authored_by: NicknameStr
    created_at: datetime
