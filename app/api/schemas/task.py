from datetime import datetime
from uuid import UUID, uuid4

from pydantic import BaseModel, Field, ConfigDict

from app.api.schemas.user import User
from app.db.models import Status


class TaskIn(BaseModel):
    title: str
    description: str
    status: Status = Field(default=Status.OPEN)


class Task(TaskIn):
    model_config = ConfigDict(from_attributes=True)

    id: UUID = Field(default_factory=uuid4)
    created_at: datetime = Field(default_factory=datetime.now)
    author: User | None = None
