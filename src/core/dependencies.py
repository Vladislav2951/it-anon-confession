from infrastructure.postgres.uow import TransactionFactory
from services import AuthService, UserService


_database_uow_factory = TransactionFactory()

_auth_service = AuthService(_database_uow_factory)
_user_service = UserService(_database_uow_factory)


def auth_srv() -> AuthService:
    return _auth_service


def user_srv() -> UserService:
    return _user_service
