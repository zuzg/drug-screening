import pandas as pd

from functools import reduce


def combine_assays(
    dataframes: list[pd.DataFrame],
    names: list[str],
    id_column: str = "CMPD ID",
    control_prefix: str = "CTRL",
):
    """
    Combine assays into a single dataframe.
    Performs initial preprocessing needed for valid merge, e.g.
    dropping controls and setting uniform ID column

    :param dataframes: list of dataframes to merge
    :param names: list of names for the dataframes
    :param id_column: name of the id column, defaults to "CMPD ID"
    :param control_prefix: prefix of control values index, defaults to "CTRL"
    :raises ValueError: if more than 1/no column(s) having id_column in file
    :return: merged dataframe (potentially with duplicates)
    """
    processed_dataframes = list()
    for df, name in zip(dataframes, names):
        if sum(df.columns.map(lambda x: id_column.upper() in x.upper())) != 1:
            raise ValueError(
                f"More than 1/no column(s) having '{id_column}' in file: {name}"
            )
        df = df.rename(str.upper, axis="columns")
        df = df.rename({df.filter(like=id_column).columns[0]: id_column}, axis=1)
        df = (
            df.drop(
                df[
                    df[id_column].apply(lambda x: str(x).startswith(control_prefix))
                ].index
            )
            .set_index(id_column)
            .add_prefix(name + " - ")
            .reset_index()
        )
        processed_dataframes.append(df)
    merged = reduce(
        lambda left, right: pd.merge(left, right, on=[id_column], how="outer"),
        processed_dataframes,
    )
    return merged
