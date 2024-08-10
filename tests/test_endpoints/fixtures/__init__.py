from uuid import uuid4
import pytest
from tests import test_session_id

@pytest.fixture
def get_test_session_id():
    return test_session_id


@pytest.fixture
def get_non_existent_session_id():
    return uuid4()
