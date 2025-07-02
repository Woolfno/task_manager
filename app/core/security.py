from datetime import datetime, timedelta
from typing import Annotated

import jwt
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from jwt.exceptions import InvalidTokenError
from passlib.context import CryptContext

from app.api.services.user import UserService, get_user_service
from app.core.config import get_settings
from app.db.models import User

pwd_ctx = CryptContext(schemes=['bcrypt'], deprecated="auto")

oauth_schema = OAuth2PasswordBearer(tokenUrl="/api/auth/token")


def verify_password(hash: str, password: str) -> bool:
    return pwd_ctx.verify(password, hash)


def get_password_hash(password: str) -> str:
    return pwd_ctx.hash(password)


async def authenticate(username: str, password: str, service: UserService) -> User | None:
    u = await service.get_by_username(username)
    if u is None:
        return None
    if verify_password(u.password, password):
        return u
    return None


async def get_current_user(token: Annotated[str, Depends(oauth_schema)],
                           service: Annotated[UserService, Depends(get_user_service)]) -> User:
    credentials_exception = HTTPException(status_code=status.HTTP_401_UNAUTHORIZED,
                                          detail="not validate username or password",
                                          headers={"WWW-Authenticate": "Bearer"})
    try:
        payload = jwt.decode(token, get_settings().SECRET_KEY,
                             algorithms=[get_settings().ALGORITHM])
        username = payload.get("sub")
        if username is None:
            raise credentials_exception
    except InvalidTokenError:
        raise credentials_exception
    u = await service.get_by_username(username)
    if u is None:
        raise credentials_exception
    return u


def create_access_token(data: dict, expires_delta: timedelta | None = None) -> str:
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.now() + expires_delta
    else:
        expire = datetime.now() + timedelta(minutes=5)
    to_encode.update({'exp': expire})
    encode_jwt = jwt.encode(to_encode, get_settings(
    ).SECRET_KEY, algorithm=get_settings().ALGORITHM)
    return encode_jwt
