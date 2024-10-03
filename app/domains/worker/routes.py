from typing import Any

from fastapi import APIRouter

from app.redis import async_redis_conn as redis_conn
from app.settings import settings

router = APIRouter()


# Worker registration
@router.post("/register", tags=["workers"])
async def register_worker(worker_info: dict[str, Any]) -> dict[str, str]:
    worker_id = worker_info.get("id")

    if not worker_id:
        return {"error": "Worker ID is required"}

    # Add worker ID to the list
    await redis_conn.rpush(settings.worker_list_key, worker_id)

    return {"message": f"Worker {worker_id} registered successfully"}


# Worker load balancing
@router.get("/next", tags=["workers"])
async def get_next_worker() -> dict[str, str]:
    """
    Get the next available worker using Redis LMOVE. Each time this endpoint is called, it will return the next worker
    from the pool of workers.
     This will be handful for load balancing.
    """
    worker_id = await redis_conn.lmove(
        settings.worker_list_key, settings.worker_list_key, "LEFT", "RIGHT"
    )

    if not worker_id:
        return {"error": "No workers available"}

    return {"worker_id": worker_id.decode("utf-8")}
