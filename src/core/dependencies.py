from infrastructure.postgres.uow import SQLAlchemyUoWFactory
from services import AuthService


_database_uow_factory = SQLAlchemyUoWFactory()

_auth_service = AuthService(_database_uow_factory)


def auth_srv() -> AuthService:
    return _auth_service
