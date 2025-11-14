from fastapi import HTTPException, Request, status
from fastapi.security import HTTPBearer

from .jwt import decode_jwt


class JWTBearer(HTTPBearer):
    def __init__(self, auto_error=True):
        super().__init__(auto_error=auto_error)

    def verify_jwt(self, token: str) -> bool:
        is_valid = False

        try:
            decoded_token = decode_jwt(token)

            if decoded_token:
                is_valid = decoded_token['type'] == 'access'
        except Exception:
            pass

        return is_valid

    async def __call__(self, request: Request) -> str:
        credentials = await super().__call__(request)

        if credentials is None:
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED,
                                detail='Invalid credentials')

        if credentials.scheme != 'Bearer':
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED,
                                detail='Invalid authentication scheme')

        if not self.verify_jwt(credentials.credentials):
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN,
                                detail='Invalid authorization code')

        return credentials.credentials

