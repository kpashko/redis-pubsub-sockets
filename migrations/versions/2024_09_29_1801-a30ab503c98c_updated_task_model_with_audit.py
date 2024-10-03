"""updated task model with audit

Revision ID: a30ab503c98c
Revises: 1bb583a87228
Create Date: 2024-09-29 18:01:26.116769

"""

from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op

# revision identifiers, used by Alembic.
revision: str = "a30ab503c98c"
down_revision: Union[str, None] = "1bb583a87228"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.add_column(
        "task",
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("CURRENT_TIMESTAMP"),
            nullable=False,
        ),
    )
    op.add_column("task", sa.Column("created_by", sa.String(), nullable=False))
    op.add_column(
        "task",
        sa.Column(
            "updated_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("CURRENT_TIMESTAMP"),
            nullable=False,
        ),
    )
    op.add_column("task", sa.Column("updated_by", sa.String(), nullable=False))
    op.add_column(
        "task", sa.Column("cancelled_at", sa.DateTime(timezone=True), nullable=True)
    )
    op.add_column("task", sa.Column("cancelled_by", sa.String(), nullable=True))
    op.create_unique_constraint(op.f("uq_task_id"), "task", ["id"])
    op.create_unique_constraint(op.f("uq_task_result_id"), "task_result", ["id"])


def downgrade() -> None:
    op.drop_constraint(op.f("uq_task_result_id"), "task_result", type_="unique")
    op.drop_constraint(op.f("uq_task_id"), "task", type_="unique")
    op.drop_column("task", "cancelled_by")
    op.drop_column("task", "cancelled_at")
    op.drop_column("task", "updated_by")
    op.drop_column("task", "updated_at")
    op.drop_column("task", "created_by")
    op.drop_column("task", "created_at")
