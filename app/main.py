from contextlib import asynccontextmanager

from fastapi import FastAPI

from app.domains.auth import routes as auth
from app.domains.monitoring import routes as monitoring
from app.domains.monitoring.manager import (
    create_redis_pubsub_context_manager,
)
from app.domains.task import routes as task
from app.domains.user import routes as user
from app.domains.worker import routes as worker


@asynccontextmanager
async def lifespan(app: FastAPI):
    redis_manager = await create_redis_pubsub_context_manager("task_updates")
    try:
        await redis_manager.setup()
        await redis_manager.start_listening()
        yield
    finally:
        await redis_manager.cleanup()


app = FastAPI(
    title="My Tech Test",
    swagger_ui_parameters={"defaultModelsExpandDepth": -1},
    lifespan=lifespan,
)


@app.get("/", include_in_schema=False)
def read_root() -> dict[str, str]:
    return {"Hello": "World"}


@app.get("/status")
def health_check() -> dict[str, str]:
    return {"status": "up"}


app.include_router(monitoring.router, prefix="/monitoring")
app.include_router(task.router, prefix="/tasks", tags=["tasks"])
app.include_router(worker.router, prefix="/workers", tags=["workers"])
app.include_router(auth.router, prefix="", tags=["auth"])
app.include_router(user.router, prefix="/users", tags=["users"])
