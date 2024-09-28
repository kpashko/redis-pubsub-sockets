from fastapi import FastAPI

from .domains.monitoring import routes as monitoring
from .domains.task import routes as task
from .domains.worker import routes as worker


app = FastAPI(
    title="My Tech Test",
    swagger_ui_parameters={"defaultModelsExpandDepth": -1},
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
