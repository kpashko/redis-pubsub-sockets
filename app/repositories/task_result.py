from contextlib import AsyncExitStack, asynccontextmanager
from typing import AsyncIterator

from sqlalchemy.dialects.postgresql import insert
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from fastapi.encoders import jsonable_encoder

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

    async def add(self, task_result: TaskResult) -> TaskResult:
        try:
            task_result_orm = TaskResultORM(
                task_id=task_result.task_id,
                result=task_result.result,
            )
            self._session.add(task_result_orm)
            await self._session.commit()
        except SQLAlchemyError as exc:
            raise RepositoryException from exc

        return task_result

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
