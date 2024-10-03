from contextlib import AsyncExitStack, asynccontextmanager
from typing import AsyncIterator

from sqlalchemy import update
from sqlalchemy.dialects.postgresql import insert
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select

from app.database import async_session_scope
from app.entities.task import Task, TaskCreate, TaskUpdate
from app.models.task import TaskORM
from app.repositories.exceptions import NotFoundException, RepositoryException


class TaskRepository:
    _model = TaskORM
    _entity = Task

    def __init__(
        self,
        session: AsyncSession,
    ):
        self._session = session

    async def add(self, task: TaskCreate) -> Task:
        table = self._model.__table__
        statement = insert(table).values(**task.dict()).returning(table)

        try:
            result = await self._session.execute(statement)
            await self._session.commit()
        except SQLAlchemyError as exc:
            raise RepositoryException from exc

        raw_data = result.fetchone()._asdict()
        created_task = Task.model_validate(raw_data)

        return created_task

    async def get(self, task_id: str) -> Task:
        statement = select(self._model).where(self._model.id == task_id)
        try:
            result = (await self._session.execute(statement)).scalars().first()
        except SQLAlchemyError as exc:
            raise RepositoryException from exc

        if not result:
            raise NotFoundException(f"Status of the task with id '{task_id}' not found")

        return Task.model_validate(result.__dict__)

    def _map_update_data(self, data: TaskUpdate) -> dict:
        return data.dict(exclude_unset=True, exclude={"id"})

    async def update(self, data: TaskUpdate):
        statement = (
            update(self._model)
            .where(self._model.id == data.id)
            .values(self._map_update_data(data))
            .returning(self._model)
        )
        try:
            result = (await self._session.execute(statement)).scalars().first()
            await self._session.commit()
        except SQLAlchemyError as exc:
            raise RepositoryException from exc

        updated_task = Task.model_validate(result.__dict__)

        return updated_task


@asynccontextmanager
async def set_up_task_repository() -> AsyncIterator[TaskRepository]:
    async with AsyncExitStack() as stack:
        async_session = await stack.enter_async_context(async_session_scope())
        yield TaskRepository(async_session)
