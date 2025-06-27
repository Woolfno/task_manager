from enum import Enum
from uuid import UUID

from pydantic import BaseModel

from app.api.schemas.task import Task


class TypeMsg(str, Enum):
    CREATE = "create"
    UPDATE = "update status"
    DELETE = "delete"


class Notification(BaseModel):
    task: Task
    type_msg: TypeMsg
