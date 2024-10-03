import json
import logging

from fastapi import APIRouter, WebSocket, WebSocketDisconnect

from app.domains.monitoring.manager import WebSocketConnectionManager
from app.redis import async_redis_conn

logger = logging.getLogger(__name__)
router = APIRouter()
manager = WebSocketConnectionManager()


@router.websocket("/task_monitor")
async def tasks_monitoring(websocket: WebSocket) -> None:
    """Monitor all tasks in real-time"""
    await websocket.accept()

    pubsub = async_redis_conn.pubsub()
    await pubsub.psubscribe("task_updates_*")

    try:
        async for message in pubsub.listen():
            if message["type"] == "message":
                data = json.loads(message["data"])
                await websocket.send_text(json.dumps(data))
    except WebSocketDisconnect:
        await pubsub.psubscribe("task_updates_*")
        logger.info("Client disconnected from tasks monitoring")


@router.websocket("/task_monitor/{task_id}")
async def single_task_monitoring(websocket: WebSocket, task_id: str) -> None:
    """Monitor a specific task in real-time"""
    await websocket.accept()

    pubsub = async_redis_conn.pubsub()
    await pubsub.subscribe(f"task_updates_{task_id}")

    try:
        async for message in pubsub.listen():
            if message["type"] == "message":
                data = json.loads(message["data"])
                await websocket.send_text(json.dumps(data))
    except WebSocketDisconnect:
        await pubsub.unsubscribe(f"task_updates_{task_id}")
        logger.info(f"Client disconnected from monitoring task {task_id}")
