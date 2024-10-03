from datetime import datetime
from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException
from rq.exceptions import InvalidJobOperation

from app.auth import get_current_user
from app.entities.task import (
    Task,
    TaskCreate,
    TaskStatus,
    TaskType,
    TaskUpdate,
)
from app.entities.user import User
from app.redis import cached, task_queue
from app.repositories.exceptions import NotFoundException
from app.repositories.task import set_up_task_repository
from app.tasks import TASK_TYPE_MAP

router = APIRouter()


# Create a new task
@router.post("/", tags=["tasks"], response_model=Task)
async def create_task(
    task_type: TaskType,
    current_user: Annotated[User, Depends(get_current_user)],
) -> None:
    task_func = TASK_TYPE_MAP.get(task_type)
    if task_func:
        job = task_queue.enqueue(task_func, 10)
    else:
        raise HTTPException(status_code=400, detail="Task type not supported")

    task_data = TaskCreate(
        id=job.id,
        created_by=current_user.id,
        updated_by=current_user.id,
        task_type=task_type,
        status=TaskStatus.QUEUED,
    )
    async with set_up_task_repository() as repo:
        task_created = await repo.add(task_data)

    return task_created


@router.patch("/{task_id}", tags=["tasks"], response_model=Task)
async def update_task(task_id: str, status: TaskStatus) -> None:
    async with set_up_task_repository() as repo:
        result = await repo.update(TaskUpdate(id=task_id, status=status))
        return result


# Retrieve the status of a given task
@router.get("/{task_id}", tags=["tasks"])
@cached(ttl=60)
async def get_task_status(task_id: str) -> dict[str, str]:
    job = task_queue.fetch_job(task_id)
    if not job:
        async with set_up_task_repository() as repo:
            try:
                task = await repo.get(task_id)
                return task.dict()
            except NotFoundException as e:
                raise HTTPException(status_code=404, detail=str(e))

    return {
        "task_id": task_id,
        "status": job.get_status(),
        "result": str(job.result),
    }


# Cancel a task
@router.delete("/{task_id}", tags=["tasks"])
async def cancel_task(
    task_id: str, current_user: Annotated[User, Depends(get_current_user)]
) -> dict[str, str]:
    job = task_queue.fetch_job(task_id)
    if not job:
        raise HTTPException(status_code=404, detail="Task not found")

    try:
        job.cancel()
    except InvalidJobOperation:
        raise HTTPException(status_code=400, detail="Task already cancelled")

    async with set_up_task_repository() as repo:
        await repo.update(
            TaskUpdate(
                id=task_id,
                status=TaskStatus.CANCELLED,
                cancelled_by=current_user.id,
                cancelled_at=datetime.now(),
            )
        )
    return {"message": f"Task {task_id} cancelled"}
