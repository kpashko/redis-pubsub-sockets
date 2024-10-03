import json
import logging

from fastapi import APIRouter, WebSocket, WebSocketDisconnect

from app.domains.monitoring.manager import WebSocketConnectionManager
from app.redis import async_redis_conn

logger = logging.getLogger(__name__)
router = APIRouter()
manager = WebSocketConnectionManager()


# Monitor all tasks in real-time
@router.websocket("/task_monitor")
async def tasks_monitoring(websocket: WebSocket) -> None:
    # Implement WebSocket connection for real-time task monitoring
    pass


# Monitor a specific task in real-time
@router.websocket("/task_monitor/{task_id}")
async def single_task_monitoring(websocket: WebSocket, task_id: str) -> None:
    pass
