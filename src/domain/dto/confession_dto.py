from typing import Optional

from pydantic import BaseModel, Field

from domain.validators import BodyString, TitleStr


class ConfessionUpdateInput(BaseModel):
    title: Optional[TitleStr] = Field(default=None)  # type: ignore[assignment]
    body: Optional[BodyString] = Field(default=None)  # type: ignore[assignment]


class ConfessionCreateInput(BaseModel):
    title: TitleStr
    body: BodyString
