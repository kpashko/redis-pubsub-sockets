from datetime import datetime
from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, status
from rq.exceptions import InvalidJobOperation

from app.auth import get_current_user
from app.domains.task import (
    Task,
    TaskApiResponse,
    TaskCancelledApiResponse,
    TaskCreate,
    TaskStatus,
    TaskType,
    TaskUpdate,
)
from app.domains.user import User
from app.redis import cached, task_queue
from app.repositories.exceptions import NotFoundException
from app.repositories.task import set_up_task_repository
from app.tasks import TASK_TYPE_MAP

router = APIRouter()


@router.post(
    "/",
    tags=["tasks"],
    response_model=Task,
    responses={status.HTTP_400_BAD_REQUEST: {"detail": "Task type not supported"}},
)
async def create_task(
    task_type: TaskType,
    current_user: Annotated[User, Depends(get_current_user)],
) -> Task:
    task_func = TASK_TYPE_MAP.get(task_type)
    if task_func:
        job = task_queue.enqueue(task_func, 10)
    else:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail="Task type not supported"
        )

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


@router.get(
    "/{task_id}",
    tags=["tasks"],
    responses={status.HTTP_404_NOT_FOUND: {"detail": "Task not found"}},
)
@cached(ttl=60)
async def get_task_status(task_id: str) -> TaskApiResponse:
    job = task_queue.fetch_job(task_id)
    if not job:
        async with set_up_task_repository() as repo:
            try:
                task = await repo.get(task_id)
                return task.dict()
            except NotFoundException as e:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND, detail=str(e)
                )

    return TaskApiResponse(
        task_id=task_id,
        status=job.get_status(),
        result=job.result,
    )


@router.delete(
    "/{task_id}",
    tags=["tasks"],
    response_model=TaskCancelledApiResponse,
    responses={
        status.HTTP_400_BAD_REQUEST: {"detail": "Task already cancelled"},
        status.HTTP_404_NOT_FOUND: {"detail": "Task not found"},
    },
)
async def cancel_task(
    task_id: str, current_user: Annotated[User, Depends(get_current_user)]
) -> TaskCancelledApiResponse:
    job = task_queue.fetch_job(task_id)
    if not job:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Task not found"
        )

    try:
        job.cancel()
    except InvalidJobOperation:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail="Task already cancelled"
        )

    async with set_up_task_repository() as repo:
        await repo.update(
            TaskUpdate(
                id=task_id,
                status=TaskStatus.CANCELLED,
                cancelled_by=current_user.id,
                cancelled_at=datetime.now(),
            )
        )
    return TaskCancelledApiResponse(message=f"Task {task_id} cancelled")
