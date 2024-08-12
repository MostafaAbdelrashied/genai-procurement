import pytest
import time
from tests.test_endpoints import client
from tests.test_endpoints.fixtures.chat_fixture import (
    chat_url,
    assert_valid_chat_output,
)


def test_short_chat_with_gpt(client, chat_url):
    chat_input = {"message": "Hi"}
    start = time.time()
    response = client.post(chat_url, json=chat_input)
    end = time.time()

    assert response.status_code == 200
    chat_output = response.json()
    assert_valid_chat_output(chat_output)
    assert end - start < 10, "Response time exceeded 10 seconds"


@pytest.mark.parametrize(
    "chat_input, expected_form_data",
    [
        (
            {"message": "Hello"},
            {
                "General Information": {
                    "Title": "",
                    "Detailed description": {
                        "Business need": "",
                        "Project scope": "",
                        "Type of contract": "",
                    },
                },
                "Financial Details": {
                    "Start Date": "",
                    "End Date": "",
                    "Expected Amount": "",
                    "Currency": "",
                },
            },
        ),
        (
            {
                "message": "I need to initiate a new procurement request with title Dashboard"
            },
            {
                "General Information": {
                    "Title": "Dashboard",
                    "Detailed description": {
                        "Business need": "",
                        "Project scope": "",
                        "Type of contract": "",
                    },
                },
                "Financial Details": {
                    "Start Date": "",
                    "End Date": "",
                    "Expected Amount": "",
                    "Currency": "",
                },
            },
        ),
        (
            {
                "message": "Business need is 'essential', scope is 'internal', type of contract is internal"
            },
            {
                "General Information": {
                    "Title": "Dashboard",
                    "Detailed description": {
                        "Business need": "essential",
                        "Project scope": "internal",
                        "Type of contract": "internal",
                    },
                },
                "Financial Details": {
                    "Start Date": "",
                    "End Date": "",
                    "Expected Amount": "",
                    "Currency": "",
                },
            },
        ),
        (
            {
                "message": "Start date is 01.01.2025, end date is 01.01.2026, expected amount is 120000, currency is 'EUR'"
            },
            {
                "Financial Details": {
                    "Start Date": "01.01.2025",
                    "End Date": "01.01.2026",
                    "Expected Amount": "120000",
                    "Currency": "EUR",
                },
            },
        ),
    ],
)
def test_long_chat_with_gpt(client, chat_url, chat_input, expected_form_data):
    response = client.post(chat_url, json=chat_input)
    assert response.status_code == 200
    chat_output = response.json()
    assert_valid_chat_output(chat_output)

    for key, value in expected_form_data.items():
        assert key in chat_output["form"]
        assert chat_output["form"][key] == value


def test_field_update_chat_with_gpt(client, chat_url):
    # First, set up the initial state
    initial_input = {"message": "Title is Dashboard"}
    response = client.post(chat_url, json=initial_input)
    assert response.status_code == 200

    # Then, update the title
    updated_chat_input = {"message": "Can you update the title to Dashboard 2.0?"}
    response = client.post(chat_url, json=updated_chat_input)
    assert response.status_code == 200

    chat_output = response.json()
    assert_valid_chat_output(chat_output)
    assert (
        chat_output["form"]["General Information"]["Title"]
        == "Dashboard 2.0"
    )
