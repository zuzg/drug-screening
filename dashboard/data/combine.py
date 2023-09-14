from functools import reduce

import numpy as np
import pandas as pd

from dashboard.data.bmg_plate import Mode, get_activation_inhibition_zscore_dict


# NOTE: to be removed
def combine_assays(
    dataframes: list[pd.DataFrame],
    names: list[str],
    id_column: str = "EOS",
    control_prefix: str = "CTRL",
):
    """
    Combine assays into a single dataframe.
    Performs initial preprocessing needed for valid merge, e.g. dropping controls and setting uniform ID column.

    :param dataframes: list of dataframes to merge
    :param names: list of names for the dataframes
    :param id_column: name of the id column, defaults to "EOS"
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


def values_array_to_column(
    values: np.ndarray, outliers: np.ndarray, column: str
) -> pd.DataFrame:
    """
    Convert a 2D numpy array of values to a dataframe with two column (well, value), but only if the corresponding
    value in outliers is not equal to 1.

    :param values: numpy array of values (both activation/inhibition and outlier mask)
    :param outliers: numpy array of outlier mask
    :param column: name of the column
    :return: dataframe with two columns
    """
    records = [
        {"Well": f"{chr(row + 65)}{(col + 1):02d}", "Value": value}
        for (row, col), value in np.ndenumerate(values)
        if outliers[row, col] != 1
    ]
    return pd.DataFrame(records).rename(columns={"Value": column})


def get_activation_inhibition_zscore_df(
    barcode: str, values_dict: dict
) -> pd.DataFrame:
    """
    Get a dataframe with activation and inhibition values.

    :param barcode: barcode of the plate
    :param values_dict: dictionary with activation and inhibition values
    :return: dataframe with activation and inhibition values
    """
    if values_dict["activation"] is not None and values_dict["inhibition"] is not None:
        df = values_array_to_column(
            values_dict["activation"], values_dict["outliers"], "% ACTIVATION"
        )
        inhibition = values_array_to_column(
            values_dict["inhibition"], values_dict["outliers"], "% INHIBITION"
        )
        df = df.merge(inhibition, on="Well")
    elif values_dict["activation"] is not None:
        df = values_array_to_column(
            values_dict["activation"], values_dict["outliers"], "% ACTIVATION"
        )
    elif values_dict["inhibition"] is not None:
        df = values_array_to_column(
            values_dict["inhibition"], values_dict["outliers"], "% INHIBITION"
        )

    z_score = values_array_to_column(
        values_dict["z_score"], values_dict["outliers"], "Z-SCORE"
    )

    df = df.merge(z_score, on="Well")
    df["Barcode"] = barcode
    df["Well"] = df["Well"].str.replace(r"0(?!$)", "", regex=True)
    return df


def reorder_bmg_echo_columns(df: pd.DataFrame) -> pd.DataFrame:
    """
    Reorder columns of the dataframe with combined bmg echo Data Frame.

    :param df: dataframe with combined bmg echo data
    :return: dataframe with reordered columns
    """

    columns = [
        "EOS",
        "Source Plate Barcode",
        "Source Well",
        "Destination Plate Barcode",
        "Destination Well",
        "Actual Volume",
    ]

    main_columns = [col for col in columns if col in df.columns]
    remaining_columns = [
        col
        for col in df.columns
        if col not in columns and col not in ["level_0", "index"]
    ]
    return df[main_columns + remaining_columns]


def combine_bmg_echo_data(
    echo_df: pd.DataFrame,
    df_stats: pd.DataFrame,
    plate_values: np.ndarray,
    modes: dict[Mode],
    echo_keys: tuple[str] = ("Destination Plate Barcode", "Destination Well"),
) -> pd.DataFrame:
    """
    Combine Echo data with activation and inhibition values.

    :param echo_df: dataframe with Echo data
    :param df_stats: dataframe containing statistics for each plate
    :param plate_values: numpy array with activation and inhibition values - shape: (#plates, 2, 16, 24)
    :param modes: dictionary with modes for each plate
    :param echo_keys: keys used to merge Echo data with activation and inhibition values #TODO: maybe not necessary and should be hard-coded?
    :return: dataframe with Echo data and activation and inhibition values
    """
    if modes is None:
        modes = dict()
    act_inh_dict = get_activation_inhibition_zscore_dict(df_stats, plate_values, modes)
    dfs = []
    for barcode, values_dict in act_inh_dict.items():
        activation_inhibition_df = get_activation_inhibition_zscore_df(
            barcode, values_dict
        )
        dfs.append(
            echo_df.merge(
                activation_inhibition_df,
                left_on=echo_keys,
                right_on=("Barcode", "Well"),
            )
        )

    bmg_echo_combined_df = pd.concat(dfs, ignore_index=True).drop(
        columns=["Barcode", "Well"]
    )
    return reorder_bmg_echo_columns(bmg_echo_combined_df)


def split_compounds_controls(df: pd.DataFrame) -> tuple[pd.DataFrame]:
    """
    Split dataframe into compounds, positive controls and negative controls.
    :param df: dataframe with compounds and controls
    :return: tuple of dataframes with compounds, positive controls and negative controls
    """
    mask = df["Destination Well"].str[-2:]
    control_pos_df = df[mask == "24"]
    control_neg_df = df[mask == "23"]
    compounds_df = df[~mask.isin(["23", "24"])]
    return compounds_df, control_pos_df, control_neg_df


def aggregate_well_plate_stats(
    df: pd.DataFrame, assign_x_coords: bool = False
) -> tuple[pd.DataFrame]:
    """
    Aggregates the statistics (mean and std) per plate needed for the plots.
    self
    :param df: dataframe with echo and bmg data combined
    :param key: key to group by
    :param assign_x_coords: whether to assign x coordinates to the plates
    :return: dataframe: echo_bmg_df with additional columns useful for
    plotting activation/inhibition/z-score and one with statistics per plate
    """

    PLATE = "Destination Plate Barcode"
    ACTIVATION = "% ACTIVATION"
    INHIBITION = "% INHIBITION"
    Z_SCORE = "Z-SCORE"

    stats_df = (
        df.groupby(PLATE)[[ACTIVATION, INHIBITION, Z_SCORE]]
        .agg(["mean", "std", "min", "max"])
        .reset_index()
    )
    stats_df.columns = [
        PLATE,
        f"{ACTIVATION}_mean",
        f"{ACTIVATION}_std",
        f"{ACTIVATION}_min",
        f"{ACTIVATION}_max",
        f"{INHIBITION}_mean",
        f"{INHIBITION}_std",
        f"{INHIBITION}_min",
        f"{INHIBITION}_max",
        f"{Z_SCORE}_mean",
        f"{Z_SCORE}_std",
        f"{Z_SCORE}_min",
        f"{Z_SCORE}_max",
    ]

    if assign_x_coords:
        for col in [ACTIVATION, INHIBITION, Z_SCORE]:
            stats_df = stats_df.sort_values(by=f"{col}_mean")  # sort by mean
            stats_df[f"{col}_x"] = range(len(stats_df))  # get the x coordinates

    return stats_df
