from pydantic import BaseModel


class Worker(BaseModel):
    id: str


class RegisterWorkerResponse(BaseModel):
    message: str = "Worker {worker_id} registered successfully"
