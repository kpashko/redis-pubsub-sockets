import sqlalchemy as sa
import uuid


def _generate_hash_id():
    return str(uuid.uuid4())


class IDMixin:
    id = sa.Column(sa.BigInteger, primary_key=True, autoincrement=True)


class HashIDMixin:
    id = sa.Column(
        sa.String,
        primary_key=True,
        default=_generate_hash_id,
        unique=True,
        nullable=False,
    )


class AuditMixin:
    created_at = sa.Column(
        sa.DateTime(timezone=True),
        nullable=False,
        server_default=sa.func.current_timestamp(),
    )
    created_by = sa.Column(sa.String, nullable=False)
    updated_at = sa.Column(
        sa.DateTime(timezone=True),
        nullable=False,
        server_default=sa.func.current_timestamp(),
        onupdate=sa.func.current_timestamp(),
    )
    updated_by = sa.Column(sa.String, nullable=False)
    cancelled_at = sa.Column(sa.DateTime(timezone=True))
    cancelled_by = sa.Column(sa.String)
