from contextlib import AbstractAsyncContextManager
from typing import Callable

from sqlalchemy.dialects.postgresql import insert
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from pydantic import ValidationError

from app.models.task import TaskORM
from app.entities.task import Task
from app.repositories.exceptions import RepositoryException, RepositoryNotFoundException


class TaskRepository:
    _model = TaskORM
    _entity = Task

    def __init__(
            self,
            session_factory: Callable[..., AbstractAsyncContextManager[AsyncSession]],
    ):
        self._session_factory = session_factory

    async def add(self, task: Task) -> Task:
        table = self._model.__table__
        statement = insert(table).values(**task.dict())

        async with self._session_factory() as session:
            try:
                await session.execute(statement)
                await session.commit()
            except SQLAlchemyError as exc:
                raise RepositoryException from exc

        return task

    async def get(self, _id: str) -> Task:
        statement = (
            select(self._model)
            .where(self._model.id == _id)
        )
        async with self._session_factory() as session:
            try:
                result = (await session.execute(statement)).scalars().first()
            except SQLAlchemyError as exc:
                raise RepositoryException from exc

        if not result:
            raise RepositoryNotFoundException(f"Task with {_id} not found")

        try:
            return Task.model_validate(result)
        except ValidationError as exc:
            raise RepositoryException from exc
