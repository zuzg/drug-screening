import pandas as pd


def validate_correlation_dataframe(corr_df: pd.DataFrame) -> None:
    """
    Validate the correlation dataframe. Raises ValueError if the dataframe is invalid.

    :param corr_df: correlation dataframe
    :raises ValueError: if the dataframe is invalid
    """
    if not corr_df.columns.is_unique:
        raise ValueError("Column names must be unique.")
    ...  # TODO: add more validation


def validate_correlation_dfs_compatible(
    corr_df1: pd.DataFrame, corr_df2: pd.DataFrame
) -> None:
    """
    Validate that the two correlation dataframes are compatible. Raises ValueError if they are not.

    :param corr_df1: first correlation dataframe
    :param corr_df2: second correlation dataframe
    :raises ValueError: if the dataframes are not compatible
    """
    if not corr_df1.columns.equals(corr_df2.columns):
        raise ValueError("Column names must be the same.")
    ...  # TODO: add more validation
