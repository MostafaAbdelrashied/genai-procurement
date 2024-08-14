import json
import tempfile

from form.utils.form_handler import (
    find_first_empty_field,
    match_if_form_updated,
    read_json,
    update_first_empty_field,
)


def test_update_first_empty_field():
    original_dict = {
        "name": "",
        "address": {"street": "", "city": "New York"},
        "phone": "",
    }
    filled_dict = {
        "name": "John Doe",
        "address": {"street": "123 Main St", "city": "Chicago"},
        "phone": "555-1234",
    }

    update_first_empty_field(original_dict, filled_dict)
    assert original_dict["name"] == "John Doe"
    assert original_dict["address"]["street"] == ""
    assert original_dict["address"]["city"] == "New York"
    assert original_dict["phone"] == ""


def test_find_first_empty_field():
    input_dict = {
        "name": "John Doe",
        "address": {"street": "", "city": "New York"},
        "phone": "",
    }

    result = find_first_empty_field(input_dict)
    assert result == ["address", "street"]


def test_match_if_form_updated_empty():
    # Example usage
    schema = {"a": "1", "b": {"c": "2", "d": "3"}, "e": "", "f": "", "h": "8"}

    updated_schema = {
        "a": "1",
        "b": {
            "c": "22",
            "d": "3",
        },
        "e": "",
        "f": "7",
        "h": "",
    }
    match_if_form_updated(schema, updated_schema)
    assert schema == {
        "a": "1",
        "b": {
            "c": "22",
            "d": "3",
        },
        "e": "",
        "f": "",
        "h": "8",
    }


def test_read_json():
    test_schema = {"name": "", "age": 0, "city": ""}

    with tempfile.NamedTemporaryFile(mode="w", delete=False) as temp_file:
        json.dump(test_schema, temp_file)
        temp_file_path = temp_file.name

    result = read_json(temp_file_path)
    assert result == test_schema
