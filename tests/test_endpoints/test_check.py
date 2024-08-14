from __future__ import annotations

import pytest

from form.db.db_tables import Message
from form.db.db_tables import Session


@pytest.mark.parametrize(
    "endpoint, expected_response",
    [
        ("/check_health", "OK"),
        ("/check_db", "OK"),
        ("/check_tables", "All tables exist in the database."),
    ],
)
def test_check_endpoints(client, endpoint, expected_response):
    response = client.get(endpoint)
    assert response.status_code == 200
    assert response.text == expected_response


@pytest.mark.parametrize(
    "table",
    [
        Message.__table__,
        Session.__table__,
    ],
)
def test_check_table_success(client, table):
    response = client.get(f"/check_table/{table}")
    assert response.status_code == 200
    assert response.text == f"Table {table} exists in the database."


def test_check_table_failure(client):
    non_existent_table = "not_a_table"
    response = client.get(f"/check_table/{non_existent_table}")
    assert response.status_code == 404
    assert response.json() == {
        "detail": f"Table {non_existent_table} does not exist in the database."
    }
