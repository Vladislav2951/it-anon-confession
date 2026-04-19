from abc import ABC

from pydantic import UUID7, BaseModel


class BaseEntity(BaseModel, ABC):
    id: UUID7
