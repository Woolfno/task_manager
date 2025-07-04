import pytest
import sqlalchemy as sa
from fastapi import status
from httpx import AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.schemas.task import Task, TaskIn
from app.api.schemas.user import UserIn
from app.db import models
from app.db.models import Status


@pytest.mark.asyncio
async def test_create_task(client: AsyncClient, session: AsyncSession, user: UserIn, access_token: str):
    t = TaskIn(title="test", description="test task")
    response = await client.post("/api/tasks/",
                                 json={"title": t.title,
                                       "description": t.description},
                                 headers={"Authorization": f"Bearer {access_token}"})
    assert response.status_code == status.HTTP_201_CREATED
    task_r = Task.model_validate(response.json())

    result = await session.execute(sa.select(models.Task).where(models.Task.id == task_r.id))
    result = result.scalar_one_or_none()
    assert result is not None
    assert result.title == t.title
    assert result.description == t.description
    assert result.status == Status.OPEN
    assert result.author.username == user.username

    await session.delete(result)
    await session.commit()


async def test_change_status(client: AsyncClient, session: AsyncSession, 
                             user, access_token:str, task: models.Task):
    new_status = Status.CLOSE
    response = await client.put(f"/api/tasks/{task.id}?status={new_status.value}",
                                headers={"Authorization": f'Bearer {access_token}'})
    assert response.status_code == status.HTTP_200_OK

    result = await session.get(models.Task, task.id)

    assert result is not None
    assert result.status == new_status


async def test_remove(client: AsyncClient, session: AsyncSession, 
                      user, access_token:str, task: models.Task):
    response = await client.delete(f"/api/tasks/{task.id}", 
                                   headers={'Authorization': f'Bearer {access_token}'})
    assert response.status_code == status.HTTP_200_OK

    result = await session.get(models.Task, task.id)
    assert result is None


async def test_list_tasks(client: AsyncClient, task: models.Task):
    response = await client.get("/api/tasks/")
    assert response.status_code == status.HTTP_200_OK

    tasks = response.json()
    tt = []
    for t in tasks:
        tt.append(Task.model_validate(t))
    assert len(tt) > 0
