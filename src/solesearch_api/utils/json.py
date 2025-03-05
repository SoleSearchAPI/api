from typing import Any


def get_from_json(json_object: dict, path: str, default: Any = None):
    """
    Get a value from a nested dictionary representing a JSON object using a dot-separated path.

    Args:
        json_object (dict): The dictionary to navigate
        path (str): A dot-separated path like "product.data.images"
        default (Any): The value to return if the path doesn't exist. Defaults to None.

    Returns:
        The value at the path, or the default value if the path doesn't exist
    """
    if not path:
        return json_object

    keys = path.split(".")
    result = json_object

    for key in keys:
        if isinstance(result, list):
            try:
                index = int(key)
                if 0 <= index < len(result):
                    result = result[index]
                else:
                    return default
            except ValueError:
                return default
        elif isinstance(result, dict) and key in result:
            result = result[key]
        else:
            return default

    return result
