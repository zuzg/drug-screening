import base64
import io
import json


def load_data_from_json(content: str | None, name: str | None) -> dict | None:
    if content is None:
        return None
    file = None

    _, extension = name.split(".")
    if extension == "json":
        _, content_string = content.split(",")
        decoded = base64.b64decode(content_string)
        file = io.StringIO(decoded.decode("utf-8"))

    loaded_data = None
    if file:
        loaded_data = json.load(file)

    return loaded_data
