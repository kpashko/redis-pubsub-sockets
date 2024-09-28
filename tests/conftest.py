from typing import Any, Generator
from unittest.mock import patch

import pytest

from app.main import app
from fastapi.testclient import TestClient


@pytest.fixture
def client() -> Any:
    return TestClient(app)


@pytest.fixture
def mock_redis() -> Generator:
    with patch("main.Redis") as mock:
        yield mock


@pytest.fixture
def mock_queue() -> Generator:
    with patch("main.Queue") as mock:
        yield mock
