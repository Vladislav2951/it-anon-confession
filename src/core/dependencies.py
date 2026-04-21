from infrastructure.postgres.uow import TransactionFactory
from services import AccessService, AuthService, SessionService, UserService


_database_uow_factory = TransactionFactory()

_auth_service = AuthService(_database_uow_factory)
_session_service = SessionService(_database_uow_factory)
_access_service = AccessService(_database_uow_factory)
_user_service = UserService(_database_uow_factory, _access_service)


def auth_srv() -> AuthService:
    return _auth_service


def session_srv() -> SessionService:
    return _session_service


def user_srv() -> UserService:
    return _user_service


def access_srv() -> AccessService:
    return _access_service
