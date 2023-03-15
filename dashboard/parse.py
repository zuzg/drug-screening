import io
import base64

import pandas as pd

from src.data.utils import is_chemical_result


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


def get_crucial_column_names(column_names: list[str]) -> list[str]:
    """
    Returns the crucial column names from a list of column names.

    :param column_names: list of column names
    :return: list of crucial column names
    """
    return [column for column in column_names if is_chemical_result(column)]


