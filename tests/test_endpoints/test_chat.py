import time

import pytest

from tests.test_endpoints import client
from tests.test_endpoints.fixtures.chat_fixture import (
    assert_valid_chat_output,
    chat_url,
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
                "general_information": {
                    "title": "",
                    "detailed_description": {
                        "business_need": "",
                        "project_scope": "",
                        "type_of_contract": "",
                    },
                },
                "financial_details": {
                    "start_date": "",
                    "end_date": "",
                    "expected_amount": "",
                    "currency": "",
                },
            },
        ),
        (
            {
                "message": "I need to initiate a new procurement request with title Dashboard"
            },
            {
                "general_information": {
                    "title": "Dashboard",
                    "detailed_description": {
                        "business_need": "",
                        "project_scope": "",
                        "type_of_contract": "",
                    },
                },
                "financial_details": {
                    "start_date": "",
                    "end_date": "",
                    "expected_amount": "",
                    "currency": "",
                },
            },
        ),
        (
            {
                "message": "business_need is 'essential', scope is 'internal', type of contract is 'internal'"
            },
            {
                "general_information": {
                    "title": "Dashboard",
                    "detailed_description": {
                        "business_need": "essential",
                        "project_scope": "internal",
                        "type_of_contract": "internal",
                    },
                },
                "financial_details": {
                    "start_date": "",
                    "end_date": "",
                    "expected_amount": "",
                    "currency": "",
                },
            },
        ),
        (
            {
                "message": "Start date is 2025-01-01, end date is 2026-01-01, expected amount is '12000', currency is 'EUR'"
            },
            {
                "financial_details": {
                    "start_date": "2025-01-01",
                    "end_date": "2026-01-01",
                    "expected_amount": "12000",
                    "currency": "EUR",
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


@pytest.mark.parametrize(
    "chat_input, expected_form_data",
    [
        (
            {
                "message": "Hello. I need to create a new procurement request with title Dashboard, business_need is 'essential', scope is 'internal', type of contract is 'ngo', start date is 2025-01-01, end date is 2026-01-01, expected amount is 30k€"
            },
            {
                "general_information": {
                    "title": "Dashboard",
                    "detailed_description": {
                        "business_need": "essential",
                        "project_scope": "internal",
                        "type_of_contract": "ngo",
                    },
                },
                "financial_details": {
                    "start_date": "2025-01-01",
                    "end_date": "2026-01-01",
                    "expected_amount": "30000",
                    "currency": "EUR",
                },
            },
        ),
    ],
)
def test_complete_chat_with_gpt(client, chat_url, chat_input, expected_form_data):
    response = client.post(chat_url, json=chat_input)
    assert response.status_code == 200
    chat_output = response.json()
    assert_valid_chat_output(chat_output)
    assert chat_output["response"] == "The form was successfully filled."
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
    assert chat_output["form"]["general_information"]["title"] == "Dashboard 2.0"
