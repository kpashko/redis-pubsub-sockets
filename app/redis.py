from redis import Redis
from redis.asyncio import Redis as AsyncRedis
from rq import Queue

from app.settings import settings

async_redis_conn = AsyncRedis(host="redis", port=6379)
redis_conn = Redis(host="redis", port=6379)

# rq only supports synchronous Redis connections
task_queue = Queue(settings.task_queue, connection=redis_conn)
