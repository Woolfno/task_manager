from typing import Annotated
from uuid import UUID

from fastapi import Depends
from sqlalchemy import delete, select
from sqlalchemy.ext.asyncio.session import AsyncSession

from app.api.schemas.task import Task, TaskIn
from app.db import models
from app.db.database import get_session


class TaskService:
    def __init__(self, session: AsyncSession) -> None:
        self.session = session

    async def get_all(self) -> list[Task]:
        result = await self.session.scalars(select(models.Task))
        return [Task.model_validate(t) for t in result.all()]

    async def get_by_id(self, id: UUID) -> Task | None:
        task = await self.session.get(models.Task, id)
        if task is None:
            return None
        return Task.model_validate(task)

    async def create(self, task: TaskIn) -> Task:
        t = models.Task(**task.model_dump())
        self.session.add(t)
        await self.session.commit()
        await self.session.flush()
        return Task.model_validate(t)

    async def update_status(self, id: UUID, status: models.Status) -> Task | None:
        task = await self.session.get(models.Task, id)
        if task is None:
            return None
        task.status = status
        await self.session.commit()
        return Task.model_validate(task)

    async def remove(self, id: UUID) -> None:
        query = delete(models.Task).where(models.Task.id == id)
        await self.session.execute(query)
        await self.session.commit()


def get_task_service(session: Annotated[AsyncSession, Depends(get_session)]) -> TaskService:
    return TaskService(session)
