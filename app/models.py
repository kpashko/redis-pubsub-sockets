from typing import Any

from pydantic import BaseModel


class User(BaseModel):
    pass


class Task(BaseModel):
    id: str
    status: str
    result: Any | None = None


class TaskResult(BaseModel):
    pass
