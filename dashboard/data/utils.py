import pandas as pd


def eos_to_ecbd_link(df: pd.DataFrame) -> pd.DataFrame:
    """
    Change eos to url to that eos in provided dataframe

    :param df: dataframe with EOS column
    :return: dataframe with eoses as urls
    """
    df_links = df.copy()
    df_links["EOS"] = df_links["EOS"].apply(
        lambda eos: f"[{eos}](https://ecbd.eu/compound/{eos})"
    )
    return df_links


def is_chemical_result(column_name: str) -> bool:
    """
    Check if column name is a chemical result one
    :param column_name: column_name to check
    :return: Whether the column contains chemical results or not
    """
    return (
        "% ACTIVATION" in column_name or "% INHIBITION" in column_name
    ) and "(" not in column_name


def get_chemical_columns(columns: list[str]) -> list[str]:
    """
    Get chemical columns from a list of columns

    :param columns: list of columns
    :return: list of chemical columns
    """
    return [column for column in columns if is_chemical_result(column)]
