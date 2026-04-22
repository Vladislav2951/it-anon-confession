from .auth_dto import LoginInput, RegisterInput
from .confession_dto import ConfessionCreateInput, ConfessionUpdateInput
from .context_dto import IdentityContext
from .role_dto import AssignPermissionInput, RoleCreateInput, RoleUpdateInput
from .user_dto import ChangePasswordUserInput, PatchUpdateUserInput


__all__ = [
    "LoginInput",
    "RegisterInput",
    "PatchUpdateUserInput",
    "ChangePasswordUserInput",
    "RoleCreateInput",
    "RoleUpdateInput",
    "IdentityContext",
    "AssignPermissionInput",
    "ConfessionUpdateInput",
    "ConfessionCreateInput",
]
