import uuid
from datetime import datetime
from enum import Enum

import sqlalchemy as sa
from sqlalchemy.sql import func
from sqlalchemy.orm import Mapped, mapped_column

from app.db.database import Base


class User(Base):
    __tablename__ = "user"

    id: Mapped[uuid.UUID] = mapped_column(
        type_=sa.types.Uuid, primary_key=True, server_default=sa.text('gen_random_uuid()'))
    username: Mapped[str]
    password: Mapped[str]


class Status(str, Enum):
    OPEN = 'open'
    INPROCESS = 'in process'
    CLOSE = 'close'


class Task(Base):
    __tablename__ = 'task'

    id: Mapped[uuid.UUID] = mapped_column(
        type_=sa.types.Uuid, primary_key=True, server_default=sa.text('gen_random_uuid()'))
    title: Mapped[str]
    description: Mapped[str]
    status: Mapped[Status] = mapped_column(sa.Enum(Status, name="status_enum"), default=Status.OPEN)
    created_at: Mapped[datetime] = mapped_column(
        type_=sa.types.DateTime, server_default=func.now())
