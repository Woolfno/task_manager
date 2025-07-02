import uuid
from datetime import datetime
from enum import Enum
from typing import Optional

import sqlalchemy as sa
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.sql import func

from app.db.database import Base


class User(Base):
    __tablename__ = "user"

    id: Mapped[uuid.UUID] = mapped_column(
        type_=sa.types.Uuid, primary_key=True, server_default=sa.text("gen_random_uuid()"))
    username: Mapped[str] = mapped_column(unique=True)
    password: Mapped[str]
    tasks: Mapped[list['Task']] = relationship(back_populates="author")


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
    status: Mapped[Status] = mapped_column(
        sa.Enum(Status, name="status_enum"), default=Status.OPEN)
    created_at: Mapped[datetime] = mapped_column(
        type_=sa.types.DateTime, server_default=func.now())
    author: Mapped[Optional[User]] = relationship(back_populates="tasks")
    author_id: Mapped[Optional[uuid.UUID]] = mapped_column(
        sa.ForeignKey("user.id"))
