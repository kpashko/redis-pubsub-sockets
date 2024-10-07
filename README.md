## Project Overview
This is an exercise in software architecture, API design, advanced Python concepts, and best practices in web development.

The task is to implement a distributed task queue system with real-time monitoring capabilities.

This system should be able to handle high concurrency, ensure fault tolerance, and provide efficient task distribution across multiple worker nodes.

## Features

1. RESTful API for task submission, status retrieval, and cancellation.
2. Distributed task queue using Redis and RQ (Redis Queue).
3. Real-time monitoring system using WebSockets for live task status updates.
4. User authentication and authorisation using JWT.
5. Worker node registration and load balancing system.
6. Distributed locking mechanisms for critical sections.
7. Result caching system to optimise performance.


## Start the application

```python3
docker compose up
```

The swagger documentation lives at http://127.0.0.1:8080/docs


## Run the tests

```python3
docker compose up tests --exit-code-from tests
```

## Run the linter

```python3
ruff check --select I --fix .  # run isort
ruff format .
```

## Using locks for long running tasks

```python3
from app.redis import get_redis, task_lock

async with get_redis() as redis_conn:
   async with task_lock(redis_conn, "my_task_lock") as lock_acquired:
       if not lock_acquired:
           raise Exception("Task already running")
       do_something()
```

## Using caching for endpoints:
```python3
from app.redis import cached

@router.get("/items/{item_id}")
@cached()
async def get_item():
    ...
```
