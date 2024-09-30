from typing import Annotated
from datetime import datetime

from app.repositories.task import set_up_task_repository
from app.repositories.task_result import set_up_task_result_repository
from app.repositories.exceptions import NotFoundException
from app.entities.task import Task, TaskCreate, TaskUpdate, TaskResult, TaskStatus
from fastapi import APIRouter, BackgroundTasks, Depends, HTTPException
from app.entities.user import User
from app.auth import get_current_user

router = APIRouter()


# Create a new task
@router.post("/", tags=["tasks"], response_model=Task)
async def create_task(
    status: TaskStatus,
    background_tasks: BackgroundTasks,
    current_user: Annotated[User, Depends(get_current_user)],
) -> None:
    task_data = TaskCreate(
        created_by=current_user.id, updated_by=current_user.id, status=status
    )
    async with set_up_task_repository() as repo:
        result = await repo.add(task_data)  # probably should convert here
        # background_tasks.add_task(repo.add, task_data)
        return result


@router.patch("/{task_id}", tags=["tasks"], response_model=Task)
async def update_task(task_id: str, status: TaskStatus) -> None:
    async with set_up_task_repository() as repo:
        result = await repo.update(TaskUpdate(id=task_id, status=status))
        return result


# @router.post("/", tags=["tasks"], response_model=Task)
# async def create_task(task_data: TaskCreate, background_tasks: BackgroundTasks):
#     task_id = str(uuid.uuid4())
#     task_status[task_id] = {"status": "queued", "result": None}
#
#     # Enqueue the task for processing
#     job = task_queue.enqueue(repo.add, task_data)
#     task_status[task_id]['status'] = 'in_progress'
#
#     return {"id": task_id, "status": "queued"}


# Retrieve the status of a given task
@router.get("/{task_id}", tags=["tasks"], response_model=TaskResult)
async def get_task_status(task_id: str) -> None:
    async with set_up_task_result_repository() as repo:
        try:
            result = await repo.get(task_id)
            return result
        except NotFoundException as e:
            raise HTTPException(status_code=404, detail=str(e))


# Cancel a task
@router.delete("/{task_id}", tags=["tasks"])
async def cancel_task(
    task_id: str, current_user: Annotated[User, Depends(get_current_user)]
) -> dict[str, str]:
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
