from datetime import datetime

from pydantic import BaseModel

from app.domains.task import TaskStatus, TaskType


class Task(BaseModel):
    id: str
    status: TaskStatus
    task_type: TaskType


class TaskCreate(BaseModel):
    id: str
    created_by: None | str = None
    updated_by: None | str = None
    status: TaskStatus = TaskStatus.QUEUED
    task_type: TaskType


class TaskUpdate(BaseModel):
    id: str
    status: TaskStatus
    updated_by: None | str = None
    updated_at: None | datetime = None
    cancelled_by: None | str = None
    cancelled_at: None | datetime = None


class TaskResult(BaseModel):
    task_id: str
    result: dict


class TaskResultCreate(BaseModel):
    task_id: str
    result: dict
