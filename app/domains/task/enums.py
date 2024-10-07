from enum import StrEnum

from rq.job import JobStatus


class TaskStatus(StrEnum):
    QUEUED = "queued"
    FINISHED = "finished"
    FAILED = "failed"
    STARTED = "started"
    DEFERRED = "deferred"
    SCHEDULED = "scheduled"
    CANCELLED = "cancelled"


class TaskType(StrEnum):
    SAMPLE = "sample"
