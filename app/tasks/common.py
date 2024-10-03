import functools
import json
from typing import Callable

from rq import get_current_job
from redis.asyncio import Redis
from app.tasks.exceptions import TaskException


async def _publish_status(redis_conn: Redis, task_id: str, status: str, result=None):
    """
    Publishes the status of the task to Redis Pub/Sub.
    """
    message = json.dumps({"task_id": task_id, "status": status, "result": result})
    await redis_conn.publish("task_updates", message)


def redis_task(redis_conn: Redis):
    """
    A decorator that publishes task status updates to Redis Pub/Sub.
    Task must be async i.e. a coroutine function.
    """

    def inner_wrapper(task_func: Callable):
        @functools.wraps(task_func)
        async def async_wrapper(*args, **kwargs):
            job = get_current_job()
            task_id = job.id

            try:
                await _publish_status(
                    redis_conn, task_id, "running"
                )  # TODO: use TaskStatus enum

                result = await task_func(*args, **kwargs)

                await _publish_status(redis_conn, task_id, "completed", result)
            except TaskException as e:
                await _publish_status(redis_conn, task_id, "failed", result=str(e))
                raise

            return result

        return async_wrapper

    return inner_wrapper
