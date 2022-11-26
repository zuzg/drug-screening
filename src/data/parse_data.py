import pandas as pd
from sklearn.preprocessing import MinMaxScaler


def parse_data(filename: str) -> pd.DataFrame:
    """
    Basic function to parse excel file passed by filename. Drops invalid entries.

    :param str: name of the file from which data will be parsed

    :return: parsed DataFrame
    """
    df = pd.read_excel(f"../data/raw/{filename}")
    if('CONTROL OUTLIER' in df):
        del df['CONTROL OUTLIER']
    if('Transfer Status' in df and len(df[df['Transfer Status'] != 'OK'])!=0):
        print(f"{filename} - deleted {len(df[df['Transfer Status'] != 'OK'])} rows with invalid Transfer Status")
        df = df[df['Transfer Status'] == 'OK']

    return df


def parse_barcode(df: pd.DataFrame) -> pd.DataFrame:
    """
    Parse dataframe to extract compound's ID.

    :param df: DataFrame with barcode

    :return: DataFrame with extracted barcode prefix and suffix
    """
    new_df = df.copy(deep=True)
    new_df[['Barcode_prefix', 'Barcode_exp', 'Barcode_suffix']] = new_df['Barcode assay plate'].str.extract(pat='(.{13})([^0-9]*)(.*)')

    return new_df


def combine_experiments(dfs: list[pd.DataFrame]) -> pd.DataFrame:
    """
    Combine experiment dataframes by ID.

    :param dfs: list of DataFrames to be mergedy by barcode

    :return: one merged DataFrame
    """
    #TODO generalize to more experiments
    new_dfs = []
    for df in dfs:
        new_dfs.append(parse_barcode(df))

    df_merged = pd.merge(*new_dfs,
                        left_on=['DTT  - compound ID', 'Barcode_prefix', 'Barcode_suffix'],
                        right_on = ['HRP - compound ID', 'Barcode_prefix', 'Barcode_suffix'])\
                        .rename(columns={'HRP - compound ID': 'Compound ID', 'VALUE_x': 'VALUE_DTT', 'VALUE_y': 'VALUE_HRP'})\
                        [['Compound ID', 'Barcode_prefix', 'Barcode_suffix', 'VALUE_DTT', 'VALUE_HRP']]

    return df_merged


def normalize_columns(df: pd.DataFrame, column_names: list[str]) -> pd.DataFrame:
    """
    Function to normalize chosen columns within dataframe.

    :param df: DataFrame with columns to normalize

    :param column_names: names of columns to be normalized

    :return: DataFrame with normalized columns
    """
    scaler = MinMaxScaler()
    df[column_names] = scaler.fit_transform(df[column_names])

    return df
