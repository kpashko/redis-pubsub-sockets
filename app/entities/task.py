from enum import StrEnum
from pydantic import BaseModel


class TaskStatus(StrEnum):
    NOT_STARTED = "not_started"
    PENDING = "pending"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"


class TaskResult(BaseModel):
    task_id: str
    result: dict


class Task(BaseModel):
    id: str
    status: TaskStatus
    result: TaskResult | None = None
