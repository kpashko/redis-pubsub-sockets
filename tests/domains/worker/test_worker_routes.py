import pytest

from app.domains.worker.entities import Worker
from app.redis import get_redis
from app.settings import settings


@pytest.mark.asyncio
class TestWorkerRoutes:
    async def test_register_worker(self, client):
        worker_data = Worker(id="test_worker")
        response = await client.post("/workers/register", json=worker_data.dict())

        assert response.status_code == 200
        assert response.json() == {
            "message": "Worker test_worker registered successfully"
        }

        async with get_redis() as redis_client:
            worker_list = await redis_client.get(settings.worker_list_key)
            assert "test_worker" in worker_list

    async def test_register_worker_wrong_input(self, client):
        worker_data = {"worker": "test"}
        response = await client.post("/workers/register", json=worker_data)

        assert response.status_code == 422

    @pytest.mark.skip("Need to fix pydantic validation issues")
    async def test_get_next_worker(self, client):
        worker_1 = Worker(id="1")
        worker_2 = Worker(id="2")

        await client.post("/workers/register", json=worker_1.dict())
        await client.post("/workers/register", json=worker_2.dict())

        response = await client.get("/workers/next")
        assert response.status_code == 200
        worker = response.json()
        assert worker["id"] == "1"

        response = await client.get("/workers/next")
        assert response.status_code == 200
        worker = response.json()
        assert worker["id"] == "2"

        response = await client.get("/workers/next")
        assert response.status_code == 200
        worker = response.json()
        assert worker["id"] == "1"

    @pytest.mark.skip("Need to fix pydantic validation issues")
    async def test_get_next_worker_no_workers(self, client):
        response = await client.get("/workers/next")

        assert response.status_code == 503
        assert response.json() == {"detail": "No workers available at the moment"}
