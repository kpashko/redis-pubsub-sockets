from fastapi import FastAPI

from app.domains.auth import routes as auth
from app.domains.monitoring import routes as monitoring
from app.domains.monitoring.manager import (
    RedisPubSubContextManagerV2,
    WebSocketConnectionManager,
)
from app.domains.task import routes as task
from app.domains.user import routes as user
from app.domains.worker import routes as worker
from app.redis import async_redis_conn

app = FastAPI(
    title="My Tech Test",
    swagger_ui_parameters={"defaultModelsExpandDepth": -1},
)

websocket_manager = WebSocketConnectionManager()
redis_manager = RedisPubSubContextManagerV2(
    websocket_manager, channel="task_updates", redis_conn=async_redis_conn
)


@app.get("/", include_in_schema=False)
def read_root() -> dict[str, str]:
    return {"Hello": "World"}


@app.get("/status")
def health_check() -> dict[str, str]:
    return {"status": "up"}


@app.on_event("startup")
async def startup_event():
    await redis_manager.setup()
    await redis_manager.start_listening()


@app.on_event("shutdown")
async def shutdown_event():
    """Clean up Redis and WebSocket connections."""
    await redis_manager.cleanup()


app.include_router(monitoring.router, prefix="/monitoring")
app.include_router(task.router, prefix="/tasks", tags=["tasks"])
app.include_router(worker.router, prefix="/workers", tags=["workers"])
app.include_router(auth.router, prefix="", tags=["auth"])
app.include_router(user.router, prefix="/users", tags=["users"])
