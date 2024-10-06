import json
import logging
from typing import Annotated

from fastapi import APIRouter, Depends, WebSocket, WebSocketDisconnect
from redis.asyncio import Redis

from app.domains.monitoring.manager import WebSocketConnectionManager
from app.redis import get_redis

logger = logging.getLogger(__name__)
router = APIRouter()
manager = WebSocketConnectionManager()


@router.websocket("/task_monitor")
async def tasks_monitoring(
    websocket: WebSocket, redis_client: Annotated[Redis, Depends(get_redis)]
) -> None:
    """Monitor all tasks in real-time"""
    await websocket.accept()

    pubsub = redis_client.pubsub()
    await pubsub.psubscribe("task_updates_*")

    try:
        async for message in pubsub.listen():
            if message["type"] == "message":
                data = json.loads(message["data"])
                await websocket.send_text(json.dumps(data))
    except WebSocketDisconnect:
        await pubsub.punsubscribe("task_updates_*")
        logger.info("Client disconnected from tasks monitoring")


@router.websocket("/task_monitor/{task_id}")
async def single_task_monitoring(
    task_id: str,
    websocket: WebSocket,
    redis_client: Annotated[Redis, Depends(get_redis)],
) -> None:
    """Monitor a specific task in real-time"""
    await websocket.accept()

    pubsub = redis_client.pubsub()
    await pubsub.subscribe(f"task_updates_{task_id}")

    try:
        async for message in pubsub.listen():
            if message["type"] == "message":
                data = json.loads(message["data"])
                await websocket.send_text(json.dumps(data))
    except WebSocketDisconnect:
        await pubsub.unsubscribe(f"task_updates_{task_id}")
        logger.info(f"Client disconnected from monitoring task {task_id}")
