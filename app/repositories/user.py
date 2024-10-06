from contextlib import asynccontextmanager
from typing import AsyncIterator

from sqlalchemy.dialects.postgresql import insert
from sqlalchemy.exc import IntegrityError, SQLAlchemyError
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select

from app.database import get_async_session
from app.domains.user.entities import User, UserCreateDB
from app.models.user import UserORM
from app.repositories.exceptions import (
    AlreadyExistsException,
    NotFoundException,
    RepositoryException,
)


class UserRepository:
    _model = UserORM
    _entity = User

    def __init__(
        self,
        session: AsyncSession,
    ):
        self._session = session

    async def add(self, user: UserCreateDB) -> User:
        table = self._model.__table__
        statement = insert(table).values(**user.dict()).returning(table)

        try:
            result = await self._session.execute(statement)
            await self._session.commit()
        except IntegrityError as exc:
            await self._session.rollback()
            raise AlreadyExistsException("User with this email already exists") from exc
        except SQLAlchemyError as exc:
            await self._session.rollback()
            raise RepositoryException from exc

        raw_data = result.fetchone()._asdict()
        created_user = User.model_validate(raw_data)
        return created_user

    async def get(self, user_id: str) -> User:
        statement = select(self._model).where(self._model.id == user_id)
        try:
            result = (await self._session.execute(statement)).scalars().first()
        except SQLAlchemyError as exc:
            raise RepositoryException from exc

        if not result:
            raise NotFoundException(f"User with id '{user_id}' not found")

        return User.model_validate(result)

    async def get_by_email(self, email: str) -> User:
        statement = select(self._model).where(self._model.email == email)
        try:
            result = (await self._session.execute(statement)).scalars().first()
        except SQLAlchemyError as exc:
            raise RepositoryException from exc

        if not result:
            raise NotFoundException(f"User with email '{email}' not found")

        return User.model_validate(result.__dict__)


@asynccontextmanager
async def set_up_user_repository() -> AsyncIterator[UserRepository]:
    async with get_async_session() as async_session:
        yield UserRepository(async_session)
