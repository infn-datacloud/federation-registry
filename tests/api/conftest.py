"""File to set tests configuration parameters and common fixtures."""

import pytest
from fastapi.testclient import TestClient

from fed_reg.main import app


@pytest.fixture
def client_without_token():
    return TestClient(app)


@pytest.fixture
def client_with_token():
    return TestClient(app, headers={"Authorization": "Bearer fake"})
