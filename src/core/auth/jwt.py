from datetime import datetime, timedelta
import time
from typing import Literal

import jwt
import pendulum
from pydantic import BaseModel

from src.core.config import settings
from src.features.companies.models import StaffRole


class TokenPair(BaseModel):
    access: str
    refresh: str

def create_token_pair(user_id: int, role: StaffRole) -> TokenPair:
    '''
    Creates a new token pair
    '''

    now = datetime.now(tz=pendulum.UTC)
    sub = f'id:{user_id}'

    access_expires_delta = now + timedelta(minutes=settings.jwt_access_expiry)
    to_encode = {
        'type': 'access',
        'sub': sub,
        'exp': access_expires_delta,
        'iat': now,
        'role': role.value 
    }
    access_token = jwt.encode(to_encode, key=settings.secret_key, algorithm=settings.jwt_algorithm)
    
    refresh_expires_delta = now + timedelta(minutes=settings.jwt_access_expiry)
    to_encode = {'type': 'refresh', 'sub': sub, 'exp': refresh_expires_delta, 'iat': now}
    refresh_token = jwt.encode(to_encode, key=settings.secret_key, algorithm=settings.jwt_algorithm)

    return TokenPair(access=access_token, refresh=refresh_token)

def decode_jwt(token: str) -> dict | None:
    '''
    Decodes a jwt token
    '''

    try:
        decoded_token = jwt.decode(token, settings.secret_key, algorithms=[settings.jwt_algorithm])
        return decoded_token if decoded_token['exp'] >= time.time() else None
    except Exception:
        return None
