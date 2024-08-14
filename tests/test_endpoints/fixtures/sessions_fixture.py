def assert_valid_session_data(session_data):
    assert isinstance(session_data, dict)
    assert "session_id" in session_data
    assert "form_data" in session_data
    assert "created_at" in session_data
    assert "last_updated_at" in session_data


def assert_valid_message(message):
    assert isinstance(message, dict)
    assert "message_id" in message
    assert "session_id" in message
    assert "prompt" in message
    assert "response" in message
    assert "created_at" in message
