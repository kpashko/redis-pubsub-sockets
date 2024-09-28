from typing import Any

from app.models import Task, TaskResult
from fastapi import APIRouter, BackgroundTasks

router = APIRouter()


# Create a new task
@router.post("/", tags=["tasks"], response_model=Task)
async def create_task(task_data: dict[str, Any], background_tasks: BackgroundTasks) -> None:
    # Enqueue task and return task ID
    pass


# Retrieve the status of a given task
@router.get("/{task_id}", tags=["tasks"], response_model=TaskResult)
async def get_task_status(task_id: str) -> None:
    # Implement task status retrieval
    pass


# Cancel a task
@router.delete("/{task_id}", tags=["tasks"])
async def cancel_task(task_id: str) -> dict[str, str]:
    # Implement task cancellation
    return {"message": f"Task {task_id} cancelled"}
