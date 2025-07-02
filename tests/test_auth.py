import sqlalchemy as sa
from httpx import AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.schemas.user import UserIn
from app.db.models import User


async def test_register(client: AsyncClient, session: AsyncSession):
    u = UserIn(username='username', password="123")
    response = await client.post(url="/api/auth/register",
                                 json={"username": u.username,
                                       "password": u.password},
                                 )
    assert response.status_code == 201

    result = await session.execute(sa.select(User).where(User.username == u.username))
    assert result is not None


async def test_login(client: AsyncClient, user: UserIn):
    response = await client.post("/api/auth/login",
                                 json={'username': user.username,
                                       'password': user.password},
                                 )
    assert response.status_code == 200
    assert response.json().get("access_token") is not None
