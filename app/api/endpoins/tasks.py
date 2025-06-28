from typing import Annotated
from uuid import UUID
from json import JSONDecodeError

from fastapi import Depends, WebSocket, WebSocketDisconnect
from fastapi import status as status_code
from fastapi.exceptions import HTTPException
from fastapi.routing import APIRouter
from pydantic import ValidationError

from app.api.schemas.message import Notification, TypeMsg
from app.api.schemas.task import Status, Task, TaskIn
from app.api.services.task import TaskService, get_task_service
from app.api.services.ws import ConnectionManager

router = APIRouter(prefix="/tasks", tags=["Tasks",])

ws_manager = ConnectionManager()


@router.get("/")
async def list_tasks(service: Annotated[TaskService, Depends(get_task_service)]) -> list[Task]:
    return await service.list()


@router.post("/")
async def create_task(task: TaskIn, service: Annotated[TaskService, Depends(get_task_service)]):
    t = await service.create(task)
    msg = Notification(type_msg=TypeMsg.CREATE, task=t)
    await ws_manager.broadcast(msg)
    return t


@router.put('/{id}')
async def change_status(id: UUID, status: Status, service: Annotated[TaskService, Depends(get_task_service)]) -> Task:
    t = await service.update_status(id, status)
    if t is None:
        raise HTTPException(status_code=status_code.HTTP_404_NOT_FOUND)
    msg = Notification(type_msg=TypeMsg.UPDATE, task=t)
    await ws_manager.broadcast(msg)
    return t


@router.delete('/{id}')
async def remove(id: UUID, service: Annotated[TaskService, Depends(get_task_service)]):
    t = await service.get(id)
    if t is None:
        return
    await service.remove(id)
    msg = Notification(type_msg=TypeMsg.DELETE, task=t)
    await ws_manager.broadcast(msg)


@router.websocket("/ws")
async def websocket_endpoint(ws: WebSocket):
    await ws_manager.connect(ws)
    try:
        while True:
            try:
                data = await ws.receive_json()
            except JSONDecodeError:
                continue
            try:
                msg = Notification.model_validate_json(data)
            except ValidationError:
                continue
            await ws_manager.broadcast(msg, ws)
    except WebSocketDisconnect:
        await ws_manager.disconnect(ws)
