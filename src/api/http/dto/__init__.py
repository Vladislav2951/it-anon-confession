from .auth_dto import LoginDTO, RegisterDTO
from .confession_dto import ConfessionCreateDTO, ConfessionUpdateDTO
from .role_dto import AssignPermissionDTO, RoleCreateDTO, RoleUpdateDTO
from .user_dto import ChangePasswordDTO, UpdateUserDTO


__all__ = [
    "LoginDTO",
    "RegisterDTO",
    "ChangePasswordDTO",
    "UpdateUserDTO",
    "RoleCreateDTO",
    "RoleUpdateDTO",
    "AssignPermissionDTO",
    "ConfessionCreateDTO",
    "ConfessionUpdateDTO",
]
