from __future__ import annotations

import pytest

from tests.test_endpoints.fixtures.sessions_fixture import assert_valid_message
from tests.test_endpoints.fixtures.sessions_fixture import assert_valid_session_data


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
    "session_id, expected_status, create_if_not_exists",
    [
        ("get_test_session_id", 200, False),
        ("get_non_existent_session_id", 404, False),
        ("get_non_existent_session_id", 200, True),
    ],
)
def test_update_session(
    client, session_id, expected_status, request, create_if_not_exists
):
    session_id = request.getfixturevalue(session_id)
    response = client.put(
        f"/sessions/update_session_form/{session_id}?create_if_not_exists={create_if_not_exists}",
        json={"key": "value"},
    )
    assert response.status_code == expected_status

    if expected_status == 200:
        session_data = response.json()
        assert_valid_session_data(session_data)
        assert session_data["form_data"] == {"key": "value"}
    else:
        assert response.json() == {"detail": f"Session {session_id} does not exist"}


@pytest.mark.parametrize(
    "session_id, expected_status",
    [
        ("get_test_session_id", 204),
        ("get_non_existent_session_id", 404),
    ],
)
def test_delete_session(client, session_id, expected_status, request):
    session_id = request.getfixturevalue(session_id)
    response = client.delete(f"/sessions/delete_session/{session_id}")
    assert response.status_code == expected_status

    if expected_status == 404:
        assert response.json() == {"detail": f"Session {session_id} does not exist"}
