from enum import Enum


class PermissionSlugs(Enum):
    users_view_self = "users:view:self"
    users_view_any = "users:view:any"

    # users_create = "users:create"

    users_update_self = "users:update:self"
    users_update_any = "users:update:any"

    users_delete_self = "users:delete:self"
    users_delete_any = "users:delete:any"
