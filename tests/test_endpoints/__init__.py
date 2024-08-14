from __future__ import annotations

import pytest
from fastapi.testclient import TestClient

from form.main import app


@pytest.fixture
def client():
    return TestClient(app)
