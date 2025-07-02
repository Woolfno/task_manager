from fastapi import WebSocket

from app.api.schemas.message import Notification


class ConnectionManager:
    def __init__(self) -> None:
        self._active_clients: list[WebSocket] = []

    async def connect(self, ws: WebSocket):
        await ws.accept()
        self._active_clients.append(ws)

    async def disconnect(self, ws: WebSocket):
        self._active_clients.remove(ws)

    async def broadcast(self, msg: Notification, me: WebSocket = None):  # type: ignore
        for client in self._active_clients:
            if client is not me:
                await client.send_json(msg.model_dump_json())
