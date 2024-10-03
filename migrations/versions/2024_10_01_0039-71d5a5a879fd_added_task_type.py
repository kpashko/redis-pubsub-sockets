"""added task type

Revision ID: 71d5a5a879fd
Revises: 2629d8734ada
Create Date: 2024-10-01 00:39:07.412395

"""

from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op

# revision identifiers, used by Alembic.
revision: str = "71d5a5a879fd"
down_revision: Union[str, None] = "2629d8734ada"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.add_column(
        "task",
        sa.Column(
            "task_type",
            sa.Enum("SAMPLE", name="tasktype", inherit_schema=True, native_enum=False),
            nullable=False,
        ),
    )


def downgrade() -> None:
    op.drop_column("task", "task_type")
