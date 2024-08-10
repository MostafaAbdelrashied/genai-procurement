import pytest
from tests import test_session_id


@pytest.fixture
def chat_url():
    return f"/chat/message?session_id={test_session_id}"


def assert_valid_chat_output(chat_output):
    assert isinstance(chat_output, dict)
    assert "response" in chat_output
    assert "form" in chat_output
