from uuid import UUID

from fastapi import WebSocket, WebSocketDisconnect
from fastapi import status as status_code
from fastapi.exceptions import HTTPException
from fastapi.routing import APIRouter

from app.api.schemas.task import Status, Task, TaskIn
from app.api.schemas.message import Notification, TypeMsg


router = APIRouter(prefix="/tasks", tags=["Tasks",])

store: dict[UUID, Task] = {}

connection_clients: list[WebSocket] = []


@router.get("/")
async def list_tasks() -> list[Task]:
    return [t for t in store.values()]


@router.post("/")
async def create_task(task: TaskIn):
    t = Task(**task.model_dump())
    store[t.id] = t
    msg = Notification(type_msg=TypeMsg.CREATE, task=t)
    await broadcast_message(msg)
    return t


@router.put('/{id}')
async def change_status(id: UUID, status: Status) -> Task:
    t = store.get(id)
    if t is None:
        raise HTTPException(status_code=status_code.HTTP_404_NOT_FOUND)
    t.status = status
    msg = Notification(type_msg=TypeMsg.UPDATE, task=t)
    await broadcast_message(msg)
    return t

@router.delete('/{id}')
async def remove(id:UUID):
    t = store[id]
    msg = Notification(type_msg=TypeMsg.DELETE, task=t)
    await broadcast_message(msg)
    del store[id]

async def broadcast_message(msg:Notification):
    for client in connection_clients:
        await client.send_json(msg.model_dump_json())


@router.websocket("/ws")
async def websocket_endpoint(ws: WebSocket):
    await ws.accept()
    connection_clients.append(ws)
    try:
        while True:
            data = await ws.receive_json()

            for client in connection_clients:
                if client is not ws:
                    await client.send_json(data)
    except WebSocketDisconnect:
        connection_clients.remove(ws)
