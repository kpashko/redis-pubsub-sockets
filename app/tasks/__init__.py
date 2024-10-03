"""This package contains tools to create and definitions of tasks"""

from app.domains.task import TaskType
from app.tasks.sample_task import sample_task

TASK_TYPE_MAP = {TaskType.SAMPLE: sample_task}
