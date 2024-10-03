from datetime import datetime
from enum import StrEnum

from pydantic import BaseModel


class TaskStatus(StrEnum):
    QUEUED = "queued"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"


class TaskType(StrEnum):
    SAMPLE = "sample"


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
