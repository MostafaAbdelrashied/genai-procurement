import pytest

from tests.test_endpoints import client
from tests.test_endpoints.fixtures import (
    get_test_session_id,
    get_non_existent_session_id,
)
from tests.test_endpoints.fixtures.sessions_fixture import (
    assert_valid_message,
    assert_valid_session_data,
)


def test_get_all_sessions(client, get_test_session_id):
    response = client.get("/sessions/get_all_sessions")
    assert response.status_code == 200
    sessions = response.json()
    assert isinstance(sessions, list)
    assert len(sessions) >= 1
    assert get_test_session_id in [session["session_id"] for session in sessions]


@pytest.mark.parametrize(
    "session_id, expected_status",
    [
        ("get_test_session_id", 200),
        ("get_non_existent_session_id", 404),
    ],
)
def test_get_session(client, session_id, expected_status, request):
    session_id = request.getfixturevalue(session_id)
    response = client.get(f"/sessions/get_session_data/{session_id}")
    assert response.status_code == expected_status

    if expected_status == 200:
        session_data = response.json()
        assert_valid_session_data(session_data)
    else:
        assert response.json() == {"detail": f"Session {session_id} does not exist"}


@pytest.mark.parametrize(
    "session_id, expected_status",
    [
        ("get_test_session_id", 200),
        ("get_non_existent_session_id", 404),
    ],
)
def test_get_session_messages(client, session_id, expected_status, request):
    session_id = request.getfixturevalue(session_id)
    response = client.get(f"/sessions/get_messages_history/{session_id}")
    assert response.status_code == expected_status

    if expected_status == 200:
        messages = response.json()
        assert isinstance(messages, list)
        assert len(messages) >= 1
        assert_valid_message(messages[0])
    else:
        assert response.json() == {"detail": f"Session {session_id} does not exist"}


@pytest.mark.parametrize(
    "session_id, expected_status",
    [
        ("get_test_session_id", 200),
        ("get_non_existent_session_id", 404),
    ],
)
def test_update_session(client, session_id, expected_status, request):
    session_id = request.getfixturevalue(session_id)
    response = client.put(
        f"/sessions/update_session_form/{session_id}",
        json={"key": "value"},
    )
    assert response.status_code == expected_status

    if expected_status == 200:
        session_data = response.json()
        assert_valid_session_data(session_data)
        assert session_data["form_data"] == {"key": "value"}
    else:
        assert response.json() == {"detail": f"Session {session_id} does not exist"}


def test_delete_session_success(client, get_test_session_id):
    response = client.delete(f"/sessions/delete_session/{get_test_session_id}")
    assert response.status_code == 204


def test_delete_session_failure(client, get_test_session_id):
    response = client.delete(f"/sessions/delete_session/{get_test_session_id}")
    assert response.status_code == 404
    assert response.json() == {
        "detail": f"Session {get_test_session_id} does not exist"
    }
