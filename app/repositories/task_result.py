from contextlib import AsyncExitStack, asynccontextmanager
from sqlalchemy.dialects.postgresql import insert
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from typing import AsyncIterator

from app.models.task import TaskResultORM
from app.entities.task import TaskResult
from app.repositories.exceptions import RepositoryException, NotFoundException
from app.database import async_session_scope


class TaskResultRepository:
    _model = TaskResultORM
    _entity = TaskResult

    def __init__(
        self,
        session: AsyncSession,
    ):
        self._session = session

    async def add(self, task: TaskResult) -> TaskResult:
        table = self._model.__table__
        statement = insert(table).values(**task.dict()).returning(table)

        try:
            result = await self._session.execute(statement)
            await self._session.commit()
        except SQLAlchemyError as exc:
            raise RepositoryException from exc

        raw_data = result.fetchone()._asdict()
        created_task = self._entity.model_validate(raw_data)

        return created_task

    async def get(self, task_id: str) -> TaskResult:
        statement = select(self._model).where(self._model.task_id == task_id)
        try:
            result = (await self._session.execute(statement)).scalars().first()
        except SQLAlchemyError as exc:
            raise RepositoryException from exc

        if not result:
            raise NotFoundException(f"Task with id '{task_id}' not found")

        return self._entity.model_validate(result.__dict__)


@asynccontextmanager
async def set_up_task_result_repository() -> AsyncIterator[TaskResultRepository]:
    async with AsyncExitStack() as stack:
        async_session = await stack.enter_async_context(async_session_scope())
        yield TaskResultRepository(async_session)
