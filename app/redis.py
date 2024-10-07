import functools
import json
import logging
import os
from contextlib import asynccontextmanager
from typing import AsyncGenerator, Callable

from redis import Redis
from redis.asyncio import Redis as AsyncRedis
from redis.exceptions import LockNotOwnedError
from rq import Queue

from app.settings import settings

CACHE_TTL = 120
LOCK_TIMEOUT = 300

logger = logging.getLogger(__name__)


@asynccontextmanager
async def get_redis() -> AsyncGenerator[AsyncRedis, None]:
    client = None
    try:
        client = await AsyncRedis.from_url(settings.redis_url, decode_responses=True)
        yield client
    except Exception as e:
        logger.error(f"Error while connecting to Redis: {e}")
    finally:
        if client:
            await client.close()


def get_sync_redis() -> Redis:
    """Returns a synchronous Redis connection for use with rq."""
    return Redis.from_url(settings.redis_url, decode_responses=True)


def get_task_queue() -> Queue:
    """Returns an rq Queue using the synchronous Redis connection."""
    red_conn = get_sync_redis()
    return Queue(settings.task_queue, connection=red_conn)


def cached(ttl: int = CACHE_TTL):
    """Simple decorator to cache the result of a function in Redis.
    Args:
        ttl (int): The time-to-live (TTL) for the cache key. Default is 120 seconds.
    Usage:
        @router.get("/items/{item_id}")\n
        @cached(ttl=60)\n
        async def read_item(item_id: int):
            ...

    """

    def decorator(func: Callable):
        @functools.wraps(func)
        async def wrapper(*args, **kwargs):
            if os.getenv("DISABLE_CACHE", "false").lower() == "true":
                return await func(*args, **kwargs)
            # Generate a unique cache key based on function name and arguments
            func_name = func.__name__
            key = f"{settings.cache_key}:{func_name}:{args}:{kwargs}"

            async with get_redis() as redis_connection:
                cached_hit = await redis_connection.get(key)
                if cached_hit:
                    print(f"Cache hit for {key}")
                    return json.loads(cached_hit)

                # Cache miss: call the function and cache the result
                print(f"Cache miss for {key}")
                result = await func(*args, **kwargs)
                await redis_connection.setex(
                    key, ttl, json.dumps(result)
                )  # Cache result with TTL
                return result

        return wrapper

    return decorator


@asynccontextmanager
async def task_lock(
    client: Redis,
    lock_name: str,
    timeout_seconds: float = LOCK_TIMEOUT,
    blocking: bool = True,
):
    """
    Create a redis lock intended for a long-running task

    The default timeout is when the task will be unlocked if not unlocked already.
    A sufficiently large value should be used to ensure it unlocks itself automatically.

    Usage:
    async with task_lock(redis_conn, "my_task_lock") as lock_acquired:
        if not lock_acquired:
            log()
            return
        do_something()
        ...
    """
    lock = client.lock(name=lock_name, timeout=timeout_seconds, thread_local=True)
    lock_acquired = False
    try:
        lock_acquired = await lock.acquire(
            token=lock_name,
            blocking=blocking,
        )

        yield lock_acquired
    finally:
        if lock_acquired:
            await release_lock(client, lock_name)


async def release_lock(client: Redis, lock_name: str):
    lock = client.lock(name=lock_name, thread_local=True)

    try:
        if await lock.locked():
            encoder = lock.redis.connection_pool.get_encoder()
            lock_token = encoder.encode(lock_name)
            await lock.do_release(lock_token)
    except LockNotOwnedError:
        logger.warning(f"Lock '{lock_name}' is not locked, no need to release...")
