"""added identity model

Revision ID: 2629d8734ada
Revises: a30ab503c98c
Create Date: 2024-09-30 00:17:35.084096

"""

from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op

# revision identifiers, used by Alembic.
revision: str = "2629d8734ada"
down_revision: Union[str, None] = "a30ab503c98c"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        "identity",
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("CURRENT_TIMESTAMP"),
            nullable=False,
        ),
        sa.Column("name", sa.String(), nullable=False),
        sa.Column("email", sa.String(), nullable=False),
        sa.Column("password", sa.String(), nullable=False),
        sa.Column("id", sa.String(), nullable=False),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("id"),
    )
    op.create_index(op.f("ix_identity_email"), "identity", ["email"], unique=True)


def downgrade() -> None:
    op.drop_index(op.f("ix_identity_email"), table_name="identity")
    op.drop_table("identity")
