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
                "1. Initiating a Sourcing Request": {
                    "New Request (Yes/No)": "",
                    "Title": "",
                    "Detailed description": {
                        "Business need": "",
                        "Project scope": "",
                        "Expected deliverables": "",
                        "Impact if not approved": "",
                        "Type of contract": "",
                        "Cost": "",
                    },
                },
            },
        ),
        (
            {"message": "I need to initiate a new procurement request"},
            {
                "1. Initiating a Sourcing Request": {
                    "New Request (Yes/No)": "Yes",
                    "Title": "",
                    "Detailed description": {
                        "Business need": "",
                        "Project scope": "",
                        "Expected deliverables": "",
                        "Impact if not approved": "",
                        "Type of contract": "",
                        "Cost": "",
                    },
                },
            },
        ),
        (
            {
                "message": "Title is Dashboard. Business need is essential, scope is internal, expected delivery is software, impact is outstanding, contract is grant, cost is 100k€"
            },
            {
                "1. Initiating a Sourcing Request": {
                    "New Request (Yes/No)": "Yes",
                    "Title": "Dashboard",
                    "Detailed description": {
                        "Business need": "essential",
                        "Project scope": "internal",
                        "Expected deliverables": "software",
                        "Impact if not approved": "outstanding",
                        "Type of contract": "grant",
                        "Cost": "100k€",
                    },
                }
            },
        ),
        (
            {
                "message": "Category is Applications, start date is 01.01.2025, end date is 01.01.2026, expected amount is 120k€"
            },
            {
                "2. Category Selection and Financial Details": {
                    "Category": "Applications",
                    "Start Date": "01.01.2025",
                    "End Date": "01.01.2026",
                    "Expected Amount": "120k€",
                }
            },
        ),
        (
            {
                "message": "Deal presenter is Mike Johnson, Available funds is 1 million, funding type is internal, cost center is G8GH, GCRS Company Details is Salesforce"
            },
            {
                "3. Deal Financials and Duration": {
                    "Deal Presenter": "Mike Johnson",
                    "Available Funds": "1 million",
                    "Funding Type": "internal",
                    "Cost Center": "G8GH",
                    "GCRS Company Details": "Salesforce",
                }
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
        chat_output["form"]["1. Initiating a Sourcing Request"]["Title"]
        == "Dashboard 2.0"
    )
