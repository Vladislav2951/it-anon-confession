from enum import Enum


class SystemRole(str, Enum):
    admin = "admin"
    user = "user"
