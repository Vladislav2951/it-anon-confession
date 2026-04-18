from services import AuthService


_auth_service = AuthService()


def auth_srv() -> AuthService:
    return _auth_service
