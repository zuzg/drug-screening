import io
import base64
import typing

import pandas as pd


def parse_contents(contents: str, filename: str) -> pd.DataFrame:
    _, content_string = contents.split(",")

    decoded = base64.b64decode(content_string)
    filename, extension = filename.split(".")
    if extension != "xlsx":
        raise ValueError("File must be an Excel file.")

    return pd.read_excel(io.BytesIO(decoded)).round(3)
