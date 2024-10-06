import logging
import time
from random import randint

from app.tasks.common import redis_task

logger = logging.getLogger(__name__)


@redis_task
async def sample_task(seconds: int) -> dict:
    logger.info(f"Task started for {seconds} seconds")

    time.sleep(seconds)
    result = randint(0, 100)
    logger.info(f"Task completed after {seconds} seconds")
    return {
        "result": result,
        "message": f"Task completed successfully after {seconds} seconds",
    }
