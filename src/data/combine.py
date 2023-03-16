import pandas as pd


from functools import reduce

from src.data.parse import parse_barcode
from src.data.utils import is_chemical_result


def rename_assay_columns(df: pd.DataFrame) -> pd.DataFrame:
    """
    Rename columns with assays activation/inhibition so the assay numbers are first
    :param df: dataframe with columns to rename
    :return: dataframe with renamed columns
    """
    df_renamed = df.copy()

    for col_name in df_renamed.columns:
        if is_chemical_result(col_name):
            parts = col_name.split("-")
            new_col_name = "".join([parts[1], " - ", parts[0]]).strip()
            df_renamed.rename(columns={col_name: new_col_name}, inplace=True)

    df_renamed.sort_index(axis=1, inplace=True)
    first_col = df_renamed.pop("CMPD ID")
    df_renamed.insert(0, "CMPD ID", first_col)
    return df_renamed


def combine_assays(
    dataframes: list[(pd.DataFrame, str)], barcode: bool = False, agg_function="max"
) -> pd.DataFrame:
    """
    Combine assays by compound ID.
    :param dfs: list of DataFrames and respective filenames
    :param barcode: value indicating checking upon the barcode
    :param agg_function: aggragation function to be applited incase of duplicated compound IDs
    :return: one merged DataFrame
    """
    d = dict()
    barcode_files = list()
    non_barcode_files = list()
    res = pd.DataFrame()

    for df, name in dataframes:
        key = name.replace(".xlsx", "")
        df = df.rename(str.upper, axis="columns")
        index_col = df.filter(like="CMPD ID").columns
        assert (
            len(index_col) == 1
        ), f"More than 1/no column(s) having 'CMPD ID' n file: {name}"

        df.rename({index_col[0]: "CMPD ID"}, axis=1, inplace=True)

        # check upon the barcode
        if barcode:
            df2 = parse_barcode(df)
            if set(df2["Barcode_suffix"].values) != {""}:
                barcode_files.append(key)
                df = df2
            else:
                non_barcode_files.append(key)

        suffix = " - " + key
        df = df.add_suffix(suffix)
        df.rename({"CMPD ID" + suffix: "CMPD ID"}, axis=1, inplace=True)
        if (df["CMPD ID"] == "CTRL NEG").any() or (df["CMPD ID"] == "CTRL POS").any():
            df = df.drop(df[df["CMPD ID"] == "CTRL NEG"].index)
            df = df.drop(df[df["CMPD ID"] == "CTRL POS"].index)

        d[key] = df

    # create ID column for the assays containing barcode suffix
    if barcode and len(barcode_files) != 0:
        for bar_file in barcode_files:
            d[bar_file]["ID"] = (
                d[bar_file][f"CMPD ID"].astype(str)
                + d[bar_file][f"Barcode_prefix - {bar_file}"]
            ) + d[bar_file][f"Barcode_suffix - {bar_file}"]

        bar_df = [d[b] for b in barcode_files]

        res = reduce(
            lambda left, right: pd.merge(left, right, on=["ID"], how="outer"), bar_df
        )

        bar_cols = res.filter(like="Barcode_").columns
        res.drop(bar_cols, axis=1, inplace=True)

    else:
        res = reduce(
            lambda left, right: pd.merge(left, right, on=["CMPD ID"], how="outer"),
            d.values(),
        )

        res = res.groupby("CMPD ID").agg(agg_function)

    res = res.reset_index(level=0)
    if not barcode:
        res = rename_assay_columns(res)
    return res
