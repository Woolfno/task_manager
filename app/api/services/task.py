from uuid import UUID

from app.api.schemas.task import Status, Task, TaskIn

store: dict[UUID, Task] = {}


class TaskService:
    async def list(self) -> list[Task]:
        return [t for t in store.values()]

    async def get(self, id: UUID) -> Task | None:
        t = store.get(id)
        return t

    async def create(self, task: TaskIn) -> Task:
        t = Task(**task.model_dump())
        store[t.id] = t
        return t

    async def update_status(self, id: UUID, status: Status) -> Task | None:
        t = store.get(id)
        if t is None:
            return None
        t.status = status
        return t

    async def remove(self, id: UUID):
        del store[id]


def get_task_service() -> TaskService:
    return TaskService()
