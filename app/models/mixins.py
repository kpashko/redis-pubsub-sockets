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
