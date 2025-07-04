import asyncio
import json

import pytest
from httpx import AsyncClient
from httpx_ws import aconnect_ws
from httpx_ws.transport import ASGIWebSocketTransport

from app.db.models import Task
from main import app

TIMEOUT = 2.0


@pytest.mark.asyncio
async def test_websocket_task_create(user, access_token: str):
    async with AsyncClient(transport=ASGIWebSocketTransport(app=app), base_url="http://test") as client:
        async with aconnect_ws('/api/tasks/ws', client=client) as websocket:
            task_data = {"title": "test", "description": "Websocket test"}
            response = await client.post("/api/tasks/",
                                         json=task_data,
                                         headers={'Authorization': f"Bearer {access_token}"})
            assert response.status_code == 201

            try:
                data = await asyncio.wait_for(websocket.receive_json(), timeout=TIMEOUT)
                data = json.loads(data)
                assert data['type_msg'] == "create"
            except asyncio.TimeoutError:
                pytest.fail("Timeout while waiting for CREATE message")


@pytest.mark.asyncio
async def test_websocket_task_change_status(task: Task, user, access_token: str):
    async with AsyncClient(transport=ASGIWebSocketTransport(app=app), base_url="http://test") as client:
        async with aconnect_ws('/api/tasks/ws', client) as websocket:
            new_status = 'in process'
            response = await client.put(f'/api/tasks/{str(task.id)}?status={new_status}',
                                        headers={'Authorization': f"Bearer {access_token}"})
            assert response.status_code == 200

            try:
                data = await asyncio.wait_for(websocket.receive_json(), timeout=TIMEOUT)
                data = json.loads(data)
                assert data['type_msg'] == "update status"
            except asyncio.TimeoutError:
                pytest.fail("Timeout while waiting for UPDATE message")


@pytest.mark.asyncio
async def test_websocket_task_delete(task: Task, user, access_token: str):
    async with AsyncClient(transport=ASGIWebSocketTransport(app=app), base_url="http://test") as client:
        async with aconnect_ws('/api/tasks/ws', client) as websocket:
            response = await client.delete(f'/api/tasks/{str(task.id)}',
                                           headers={'Authorization': f"Bearer {access_token}"})
            assert response.status_code == 200

            try:
                data = await asyncio.wait_for(websocket.receive_json(), timeout=TIMEOUT)
                data = json.loads(data)
                assert data['type_msg'] == "delete"
            except asyncio.TimeoutError:
                pytest.fail("Timeout while waiting for DELETE message")
