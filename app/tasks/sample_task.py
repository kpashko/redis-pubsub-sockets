import time
import logging

from app.redis import async_redis_conn
from app.tasks.common import redis_task

logger = logging.getLogger(__name__)


@redis_task(async_redis_conn)
async def sample_task(seconds: int):
    logger.info(f"Task started for {seconds} seconds")

    time.sleep(seconds)

    logger.info(f"Task completed after {seconds} seconds")
