import io
import base64

import pandas as pd


def parse_excel_assay(path_to_file: str) -> pd.DataFrame:
    """
    Parse excel file describing an experiment. Drops invalid entries.

    :param str: name of the file from which data will be parsed
    :return: parsed DataFrame
    """
    df = pd.read_excel(path_to_file)
    if "CONTROL OUTLIER" in df:
        del df["CONTROL OUTLIER"]
    if "Transfer Status" in df and len(df[df["Transfer Status"] != "OK"]) != 0:
        print(
            f"{path_to_file} - deleted {len(df[df['Transfer Status'] != 'OK'])} rows with invalid Transfer Status"
        )
        df = df[df["Transfer Status"] == "OK"]
    return df


def parse_bytes_to_dataframe(contents: str, filename: str) -> pd.DataFrame:
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

    return pd.read_excel(io.BytesIO(decoded))
