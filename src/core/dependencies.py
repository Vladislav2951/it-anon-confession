from infrastructure.postgres.uow import TransactionFactory
from services import (
    AccessService,
    AuthService,
    BusinessElementService,
    ConfessionService,
    PermissionService,
    RoleService,
    SessionService,
    UserService,
)


_database_uow_factory = TransactionFactory()

_auth_service = AuthService(_database_uow_factory)
_session_service = SessionService(_database_uow_factory)

_access_service = AccessService(_database_uow_factory)

_role_service = RoleService(_database_uow_factory, _access_service)
_permission_service = PermissionService(_database_uow_factory, _access_service)
_user_service = UserService(_database_uow_factory, _access_service)
_confession_service = ConfessionService(_database_uow_factory, _access_service)
_business_element_service = BusinessElementService(_database_uow_factory, _access_service)


def auth_srv() -> AuthService:
    return _auth_service


def session_srv() -> SessionService:
    return _session_service


def user_srv() -> UserService:
    return _user_service


def access_srv() -> AccessService:
    return _access_service


def role_srv() -> RoleService:
    return _role_service


def confession_srv() -> ConfessionService:
    return _confession_service


def permission_srv() -> PermissionService:
    return _permission_service


def business_element_srv() -> BusinessElementService:
    return _business_element_service
