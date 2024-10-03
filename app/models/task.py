import sqlalchemy as sa
from sqlalchemy.dialects.postgresql import JSONB

from app.entities.task import TaskStatus, TaskType
from app.models.base import Base
from app.models.mixins import AuditMixin, HashIDMixin


class TaskORM(Base, AuditMixin):
    __tablename__ = "task"

    id = sa.Column(
        sa.String,
        primary_key=True,
        unique=True,
        nullable=False,
    )
    status = sa.Column(
        sa.Enum(TaskStatus, inherit_schema=True, native_enum=False),
        nullable=False,
        default=TaskStatus.QUEUED,
    )
    task_type = sa.Column(
        sa.Enum(TaskType, inherit_schema=True, native_enum=False), nullable=False
    )


class TaskResultORM(Base, HashIDMixin):
    __tablename__ = "task_result"

    task_id = sa.Column(
        sa.String, sa.ForeignKey("task.id", ondelete="CASCADE"), nullable=False
    )
    result = sa.Column(JSONB, nullable=False, server_default="{}")
