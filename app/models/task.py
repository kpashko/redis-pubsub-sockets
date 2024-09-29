from app.models.base import Base
from app.models.mixins import HashIDMixin

import sqlalchemy as sa
from sqlalchemy.dialects.postgresql import JSONB

from app.entities.task import TaskStatus


class TaskORM(Base, HashIDMixin):
    __tablename__ = "task"

    status = sa.Column(
        sa.Enum(TaskStatus, inherit_schema=True, native_enum=False),
        nullable=False,
        default=TaskStatus.NOT_STARTED,
    )


class TaskResultORM(Base, HashIDMixin):
    __tablename__ = "task_result"

    task_id = sa.Column(sa.String, sa.ForeignKey("task.id"), nullable=False)
    result = sa.Column(JSONB, nullable=False, server_default="{}")
