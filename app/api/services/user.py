from typing import Annotated

import sqlalchemy as sa
from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.schemas.user import User
from app.db import models
from app.db.database import get_session


class UserService:
    def __init__(self, session: AsyncSession) -> None:
        self.session = session

    async def get_by_username(self, username: str) -> models.User | None:
        query = sa.select(models.User).where(models.User.username == username)
        result = await self.session.execute(query)
        user = result.scalar_one_or_none()
        return user

    async def create(self, username: str, password: str) -> User:
        user = models.User(username=username, password=password)
        self.session.add(user)
        await self.session.commit()
        await self.session.flush()
        return User.model_validate(user)


def get_user_service(session: Annotated[AsyncSession, Depends(get_session)]) -> UserService:
    return UserService(session)
