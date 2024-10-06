import asyncio
import json
import logging

from fastapi import WebSocket

from app.domains.task import TaskResult, TaskUpdate
from app.redis import get_redis
from app.repositories.task import set_up_task_repository
from app.repositories.task_result import set_up_task_result_repository


class WebSocketConnectionManager:
    """
    Manage WebSocket connections and broadcast messages to all connected clients
    """

    def __init__(self):
        self.active_connections: list[WebSocket] = []
        self.logger = logging.getLogger(self.__class__.__name__)

    async def connect(self, websocket: WebSocket):
        await websocket.accept()
        self.active_connections.append(websocket)
        self.logger.info(
            f"WebSocket connected. {len(self.active_connections)} active connections."
        )

    def disconnect(self, websocket: WebSocket):
        self.active_connections.remove(websocket)
        self.logger.info(
            f"WebSocket disconnected. {len(self.active_connections)} active connections."
        )

    async def broadcast(self, message: str):
        self.logger.info(
            f"Broadcasting message to {len(self.active_connections)} active connections."
        )
        for connection in self.active_connections:
            await connection.send_text(message)

    async def send_personal_message(self, message: str, websocket: WebSocket):
        await websocket.send_text(message)


class RedisPubSubContextManagerV2:
    def __init__(self, connection_manager, channel: str, redis_conn):
        self.connection_manager = connection_manager
        self.channel = channel
        self.redis_conn = redis_conn
        self.pubsub = redis_conn.pubsub()
        self.listener_task = None
        self.logger = logging.getLogger(self.__class__.__name__)

    async def setup(self):
        """Set up Redis connection and subscribe to the channel."""
        self.logger.info(f"Subscribing to {self.channel}_*")
        await self.pubsub.psubscribe(f"{self.channel}_*")

    async def start_listening(self):
        """Start the Redis Pub/Sub listener using asyncio.create_task."""

        async def handle_message(message):
            if message and message["type"] == "message":
                task_data = json.loads(message["data"])

                task_id = task_data.get("task_id")
                status = task_data.get("status")
                result: dict = task_data.get("result")

                if not task_id or not status:
                    self.logger.error(f"Unable to parse message from queue: {message}")
                    return

                async with set_up_task_repository() as task_repo:
                    await task_repo.update(TaskUpdate(id=task_id, status=status))
                if result:
                    async with set_up_task_result_repository() as task_result_repo:
                        await task_result_repo.add(
                            TaskResult(task_id=task_id, result=result)
                        )
                await self.connection_manager.broadcast(message["data"])

        async def listen():
            self.logger.info("Listening to Redis Pub/Sub...")
            async for message in self.pubsub.listen():
                self.logger.info(f"Message received: {message}")
                await handle_message(message)

        # Run the Pub/Sub listener as an asyncio task
        self.listener_task = asyncio.create_task(listen())

    async def cleanup(self):
        """Stop the listener task and clean up Redis resources."""
        self.logger.info("Starting cleanup...")

        # Cancel the task if it's running
        if self.listener_task:
            self.listener_task.cancel()
            try:
                await self.listener_task
            except asyncio.CancelledError:
                self.logger.info("Listener task cancelled.")

        if self.pubsub:
            await self.pubsub.unsubscribe(self.channel)
            self.logger.info(f"Unsubscribed from Redis channel: {self.channel}")

        if self.redis_conn:
            await self.redis_conn.aclose()
            self.logger.info("Closed Redis connection.")


async def create_redis_pubsub_context_manager(
    channel: str = "task_updates",
) -> RedisPubSubContextManagerV2:
    async for redis_conn in get_redis():
        return RedisPubSubContextManagerV2(
            connection_manager=WebSocketConnectionManager(),
            channel=channel,
            redis_conn=redis_conn,
        )
