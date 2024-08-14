from uuid import UUID

import pytest

from form.utils.text_handler import convert_str_to_uuid


def test_convert_str_to_uuid_empty_string():
    with pytest.raises(ValueError, match="String ID cannot be empty."):
        convert_str_to_uuid("")


def test_convert_str_to_uuid_valid_string():
    result = convert_str_to_uuid("test_string")
    assert isinstance(result, UUID)
    assert str(result) == "3474851a-3410-9066-97ec-77337df7aae4"


def test_convert_str_to_uuid_valid_uuid():
    uuid_obj = UUID("098f6bcd-4621-3373-8ade-4e832627b4f6")
    result = convert_str_to_uuid(uuid_obj)
    assert result == uuid_obj


def test_convert_str_to_uuid_different_strings():
    assert convert_str_to_uuid("hello") != convert_str_to_uuid("world")


def test_convert_str_to_uuid_long_string():
    long_string = "a" * 1000
    result = convert_str_to_uuid(long_string)
    assert isinstance(result, UUID)
    assert str(result) == "cabe45dc-c9ae-5b66-ba86-600cca6b8ba8"
