from fastapi.requests import HTTPConnection
from starlette.authentication import (AuthCredentials, AuthenticationBackend,
                                      AuthenticationError)

from src.core.database import SessionLocal
from src.features.auth.models import UserModel
from src.features.auth.repo import UserRepo

from .jwt import decode_jwt


class BearerTokenAuthBackend(AuthenticationBackend):
    async def authenticate(self, conn: HTTPConnection) -> tuple[AuthCredentials, UserModel] | None:
        '''
        This is here to simply inject the user model into the request if possible.
        
        If the token is invalid, the user is not injected.
        This does not actually authenticate the user 🙂
        '''

        if 'Authorization' not in conn.headers:
            return
        
        auth = conn.headers['Authorization']
        try:
            scheme, token = auth.split()
            if scheme.lower() != 'bearer':
                return

            decoded = decode_jwt(token)
            if decoded is None:
                return None
        except Exception:
            return None

        user_id = decoded['sub'].split(':')[-1]

        db = SessionLocal()
        try:
            repo = UserRepo(db)
            user = repo.get_by_id(user_id)
        finally:
            db.close()

        if user is None:
            return None

        return AuthCredentials(['authenticated']), user
