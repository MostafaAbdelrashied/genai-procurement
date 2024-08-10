import pytest
from fastapi.testclient import TestClient
from procurement.main import app


@pytest.fixture
def client():
    return TestClient(app)
