from enum import Enum


class PermissionSlugs(Enum):
    users_view = "users:view"
    users_create = "users:create"
    users_delete = "users:delete"
