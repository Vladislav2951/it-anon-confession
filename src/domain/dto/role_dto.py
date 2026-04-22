from pydantic import UUID7, BaseModel, Field

from domain.validators import NameStr


class RoleCreateInput(BaseModel):
    name: NameStr


class RoleUpdateInput(BaseModel):
    name: NameStr = Field(default=None)  # type: ignore[assignment]


class AssignPermissionInput(BaseModel):
    permission_id: UUID7
