import io
import base64

import pandas as pd


def parse_contents(contents: str, filename: str) -> pd.DataFrame:
    """
    Parses the contents of an uploaded file into a pandas DataFrame.

    :param contents: binary encoded file
    :param filename: name of the file
    :raises ValueError: if the file is not an Excel file
    :return: pandas DataFrame
    """
    filename, extension = filename.split(".")
    if extension != "xlsx":
        raise ValueError("File must be an Excel file.")

    _, content_string = contents.split(",")
    decoded = base64.b64decode(content_string)

    return pd.read_excel(io.BytesIO(decoded)).round(3)
