from datetime import datetime
from enum import StrEnum
from pydantic import BaseModel


class TaskStatus(StrEnum):
    NOT_STARTED = "not_started"
    PENDING = "pending"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"


class Task(BaseModel):
    id: str
    status: TaskStatus


class TaskCreate(BaseModel):
    created_by: None | str = None
    updated_by: None | str = None
    status: TaskStatus = TaskStatus.NOT_STARTED


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
