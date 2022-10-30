import pandas as pd
from sklearn.preprocessing import MinMaxScaler


def parse_data(filename: str) -> pd.DataFrame:
    """
    Basic function to parse excel file passed by filename. Drops invalid entries.
    """
    df = pd.read_excel(f"../data/raw/{filename}")
    del df['CONTROL OUTLIER']
    print(f"Deleted {len(df[df['Transfer Status'] != 'OK'])} rows with invalid Transfer Status")
    df = df[df['Transfer Status'] == 'OK']

    return df


def parse_barcode(df: pd.DataFrame) -> pd.DataFrame:
    """
    Parse dataframe to extract compound's ID.
    """
    df[['Barcode_prefix', 'Barcode_exp', 'Barcode_suffix']] = df['Barcode assay plate'].str.extract(pat='(.{13})([^0-9]*)(.*)')

    return df


def combine_experiments(dfs: list) -> pd.DataFrame:
    """
    Combine experiment dataframes by ID.
    """
    #TODO generalize to more experiments
    for df in dfs:
        df = parse_barcode(df)

    df_merged = pd.merge(*dfs,
                        left_on=['DTT  - compound ID', 'Barcode_prefix', 'Barcode_suffix'],
                        right_on = ['HRP - compound ID', 'Barcode_prefix', 'Barcode_suffix'])\
                        .rename(columns={'HRP - compound ID': 'Compound ID', 'VALUE_x': 'VALUE_DTT', 'VALUE_y': 'VALUE_HRP'})\
                        [['Compound ID', 'Barcode_prefix', 'Barcode_suffix', 'VALUE_DTT', 'VALUE_HRP']]

    return df_merged


def normalize_columns(df: pd.DataFrame, column_names: list) -> pd.DataFrame:
    """
    Function to normalize chosen columns within dataframe.
    """
    scaler = MinMaxScaler()
    df[column_names] = scaler.fit_transform(df[column_names])

    return df
