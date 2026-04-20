from dataclasses import dataclass
from typing import Optional

from domain.validators import NameStr


@dataclass(frozen=True, slots=True)
class UserFilter:
    roles: Optional[list[NameStr]] = None
