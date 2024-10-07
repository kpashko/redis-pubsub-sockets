import pytest
from httpx import AsyncClient

from app.auth import get_current_user
from app.domains.task import TaskStatus, TaskType
from app.domains.user import User
from app.main import app


def mock_jwt_get_user() -> User:
    return User(
        id="1",
        name="test_user",
        password="test_password",
        email="test_user@example.com",
    )


app.dependency_overrides[get_current_user] = mock_jwt_get_user


@pytest.mark.asyncio
class TestTaskRoutes:
    async def test_create_task(self, client: AsyncClient):
        response = await client.post("/tasks/", params={"task_type": TaskType.SAMPLE})
        data = response.json()
        assert response.status_code == 200
        assert data["id"]
        assert data["status"] == TaskStatus.QUEUED
        assert data["task_type"] == TaskType.SAMPLE

    async def test_create_tasks(self, client: AsyncClient):
        response = await client.post("/tasks/", params={"task_type": TaskType.SAMPLE})
        response2 = await client.post("/tasks/", params={"task_type": TaskType.SAMPLE})

        assert response.status_code == 200
        assert response2.status_code == 200
        assert response.json()["id"] != response2.json()["id"]

    async def test_create_task_with_invalid_type(self, client: AsyncClient):
        response = await client.post("/tasks/", params={"task_type": "invalid_type"})
        assert response.status_code == 422

    async def test_get_task_status(self, client: AsyncClient):
        response = await client.post("/tasks/", params={"task_type": TaskType.SAMPLE})
        task_id = response.json()["id"]
        response2 = await client.get(f"/tasks/{task_id}")
        assert response2.status_code == 200
        assert response2.json()["status"] == TaskStatus.QUEUED
