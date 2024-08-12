import json


def update_first_empty_field(original_dict: dict, filled_dict: dict) -> None:
    """Update the first empty field in a nested dict with the corresponding value from another dict.

    Args:
        original_dict (dict): The original nested dict to be modified in-place.
        filled_dict (dict): The dict containing the filled fields.
    """

    def recursive_update(original_rec_dict: dict, filled_rec_dict: dict) -> bool:
        for key, value in original_rec_dict.items():
            if isinstance(value, dict):
                if recursive_update(value, filled_rec_dict.get(key, {})):
                    return True
            elif value == "" and filled_rec_dict.get(key, "") != "":
                original_rec_dict[key] = filled_rec_dict[key]
                return True
        return False

    recursive_update(original_dict, filled_dict)


def find_first_empty_field(input_dict: dict) -> list:
    """Find the path to the first empty field in a nested dict.

    Args:
        input_dict (dict): The nested dict.

    Returns:
        list: The path to the first empty field.
    """

    def recursive_find(current_dict, current_path):
        for key, value in current_dict.items():
            new_path = current_path + [key]
            if isinstance(value, dict):
                result = recursive_find(value, new_path)
                if result:
                    return result
            elif value == "":
                return new_path
        return None

    return recursive_find(input_dict, [])


def find_rule_validation(input_dict: dict, field_path: list) -> str:
    """Find the rule for a field in a nested dict.

    Args:
        input_dict (dict): The nested dict.
        field_path (list): The path to the field.

    Returns:
        str: The rule for the field.
    """

    def recursive_find(current_dict, current_path):
        for key, value in current_dict.items():
            new_path = current_path + [key]
            if new_path == field_path:
                return value
            elif isinstance(value, dict):
                result = recursive_find(value, new_path)
                if result:
                    return result
        return None

    return recursive_find(input_dict, [])


def match_if_form_updated(schema, updated_schema):
    """Recursively update a schema with values from another schema.

    Args:
        schema (dict): The original schema.
        updated_schema (dict): The schema containing the updated values.
    """
    for key, value in updated_schema.items():
        if key in schema:
            if isinstance(value, dict) and isinstance(schema[key], dict):
                # Recursively update nested dictionaries
                match_if_form_updated(schema[key], value)
            elif schema[key] != value and (schema[key] != "" and value != ""):
                # Update mismatched values, but preserve empty strings in schema
                schema[key] = value
        else:
            # Add new key-value pairs
            schema[key] = value


def update_form_fields(schema, condition_key, condition_value, actions):
    """Recursively update a schema with values from another schema and modify schema based on conditions.

    Args:
        schema (dict): The original schema to be updated.
        condition_key (str): The key whose value needs to be checked against condition_value.
        condition_value (str): The value that condition_key should have to trigger actions.
        actions (list of tuples): List of (new_key, new_value) to be added if condition is met.
    """
    keys_to_add = []

    for key, value in schema.items():
        if isinstance(value, dict):
            update_form_fields(value, condition_key, condition_value, actions)
        elif key == condition_key and value == condition_value:
            keys_to_add.extend(actions)
        elif value == "":
            schema[key] = ""

    # Update dictionary after iteration
    for new_key, new_value in keys_to_add:
        schema[new_key] = new_value


def read_json(path: str) -> dict:
    """get the form fields from a json file

    Args:
        path (str): path to the json file

    Returns:
        dict: the form fields
    """
    with open(path, "r") as f:
        form = json.load(f)
    return form
