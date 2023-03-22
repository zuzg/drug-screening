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


def parse_barcode(df: pd.DataFrame) -> pd.DataFrame:
    """
    Parse dataframe to extract compound's ID.

    :param df: DataFrame with barcode
    :return: DataFrame with extracted barcode prefix and suffix
    """
    bar_colname = "Barcode assay plate"
    temp = df.filter(like="BARCODE ASSAY PLATE").columns
    if len(temp != 0):
        bar_colname = temp[0]

    new_df = df.copy(deep=True)
    new_df[["Barcode_prefix", "Barcode_exp", "Barcode_suffix"]] = new_df[
        bar_colname
    ].str.extract(pat="(.{13})([^0-9]*)(.*)")
    return new_df
