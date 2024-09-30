"""Basic model for user of the service"""

import sqlalchemy as sa

from app.models.base import Base
from app.models.mixins import HashIDMixin


class UserORM(Base, HashIDMixin):
    __tablename__ = "identity"

    created_at = sa.Column(
        sa.DateTime(timezone=True),
        nullable=False,
        server_default=sa.func.current_timestamp(),
    )
    name = sa.Column(sa.String, nullable=False)
    email = sa.Column(sa.String, nullable=False, unique=True, index=True)
    password = sa.Column(sa.String, nullable=False)
