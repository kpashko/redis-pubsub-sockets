import functools
import json
from typing import Awaitable, Callable

from redis.asyncio import Redis
from rq import get_current_job

from app.domains.task import TaskStatus
from app.redis import get_redis
from app.tasks.exceptions import TaskException


async def _publish_status(redis_conn: Redis, task_id: str, status: str, result=None):
    """
    Publishes the status of the task to Redis Pub/Sub.
    """
    message = json.dumps({"task_id": task_id, "status": status, "result": result})
    await redis_conn.publish(f"task_updates_{task_id}", message)


def redis_task(task_func: Callable[..., Awaitable]):
    """
    A decorator that publishes task status updates to Redis Pub/Sub.
    Task must be async i.e. a coroutine function.
    """

    @functools.wraps(task_func)
    async def async_wrapper(*args, **kwargs):
        job = get_current_job()
        task_id = job.id

        async with get_redis() as redis_conn:
            try:
                await _publish_status(redis_conn, task_id, TaskStatus.RUNNING)

                result = await task_func(*args, **kwargs)

                await _publish_status(redis_conn, task_id, TaskStatus.COMPLETED, result)
            except TaskException as e:
                await _publish_status(
                    redis_conn, task_id, TaskStatus.FAILED, result=str(e)
                )
                raise

            return result

    return async_wrapper
