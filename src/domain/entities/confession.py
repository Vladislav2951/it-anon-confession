from datetime import datetime, timezone
from typing import Self

from pydantic import UUID7, ConfigDict
from uuid_extensions import uuid7  # type: ignore[import-untyped]

from domain.entities import BaseEntity
from domain.validators import BodyString, NicknameStr, TitleStr


class Confession(BaseEntity):
    title: TitleStr
    body: BodyString
    authored_by: NicknameStr
    user_id: UUID7
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)

    @classmethod
    def create(
        cls, title: TitleStr, body: BodyString, authored_by: NicknameStr, user_id: UUID7
    ) -> Self:
        now = datetime.now(timezone.utc)
        return cls(
            id=uuid7(),
            title=title,
            body=body,
            authored_by=authored_by,
            user_id=user_id,
            created_at=now,
        )
