from datetime import timedelta
from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm

from app.api.schemas.token import Token
from app.api.schemas.user import User, UserIn
from app.api.services.user import UserService, get_user_service
from app.core.config import get_settings
from app.core.security import (authenticate, create_access_token,
                               get_password_hash)

router = APIRouter(prefix="/auth", tags=["Authentication"])


@router.post("/register", status_code=status.HTTP_201_CREATED)
async def register(user: UserIn, service: Annotated[UserService, Depends(get_user_service)]) -> User:
    u = await service.get_by_username(user.username)
    if u is not None:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail="username is exist")
    u = await service.create(user.username, get_password_hash(user.password))
    return u


@router.post("/login")
async def login(user: UserIn, service: Annotated[UserService, Depends(get_user_service)]) -> Token:
    u = await authenticate(user.username, user.password, service)
    if u is None:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED,
                            detail="incorrect username or password",
                            headers={"WWW-Authenticate": "Bearer"})
    expires = timedelta(minutes=get_settings().ACCESS_TOKEN_EXPIRE)
    token = create_access_token(
        data={"sub": u.username}, expires_delta=expires)
    return Token(access_token=token)


@router.post('/token')
async def token(form_data: Annotated[OAuth2PasswordRequestForm, Depends()],
                service: Annotated[UserService, Depends(get_user_service)]) -> Token:
    return await login(UserIn(username=form_data.username, password=form_data.password),
                       service)
