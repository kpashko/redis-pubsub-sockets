from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, status
from redis.asyncio import Redis

from app.api import ResponseErrorSchema
from app.domains.worker import RegisterWorkerResponse, Worker
from app.redis import get_redis
from app.settings import settings

router = APIRouter()


# Worker registration
@router.post("/register", tags=["workers"], response_model=RegisterWorkerResponse)
async def register_worker(
    worker: Worker, redis_client: Annotated[Redis, Depends(get_redis)]
) -> RegisterWorkerResponse:
    await redis_client.rpush(settings.worker_list_key, worker.id)

    return RegisterWorkerResponse(message=f"Worker {worker.id} registered successfully")


# Worker load balancing
@router.get(
    "/next",
    tags=["workers"],
    response_model=Worker,
    responses={
        status.HTTP_503_SERVICE_UNAVAILABLE: {
            "model": ResponseErrorSchema,
            "detail": "No workers available at the moment",
        }
    },
)
async def get_next_worker(redis_client: Annotated[Redis, Depends(get_redis)]) -> Worker:
    """
    Get the next available worker using Redis LMOVE. Each time this endpoint is called, it will return the next worker
    from the pool of workers.
     This will be handful for load balancing.
    """
    worker_id = await redis_client.lmove(
        settings.worker_list_key, settings.worker_list_key, "LEFT", "RIGHT"
    )

    if not worker_id:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="No workers available at the moment",
        )

    return Worker(id=worker_id.decode("utf-8"))
