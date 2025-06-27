from datetime import datetime
from enum import Enum
from uuid import UUID, uuid4
from pydantic import BaseModel, Field

from app.api.schemas.user import User


class Status(str, Enum):
    OPEN = 'open'
    INPROCESS = 'in process'
    CLOSE = 'close'


class TaskIn(BaseModel):
    title: str
    description: str
    status: Status = Field(default=Status.OPEN)


class Task(TaskIn):
    id:UUID = Field(default_factory=uuid4)
    created_at: datetime = Field(default_factory=datetime.now)
    author: User | None = None
