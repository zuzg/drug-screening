import copy
import pandas as pd
from sklearn.preprocessing import MinMaxScaler
from functools import reduce


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
    new_dfs = []
    for df in dfs:
        new_dfs.append(parse_barcode(df))

    df_merged = pd.merge(*new_dfs,
                        left_on=['DTT  - compound ID', 'Barcode_prefix', 'Barcode_suffix'],
                        right_on = ['HRP - compound ID', 'Barcode_prefix', 'Barcode_suffix'])\
                        .rename(columns={'HRP - compound ID': 'Compound ID', 'VALUE_x': 'VALUE_DTT', 'VALUE_y': 'VALUE_HRP'})\
                        [['Compound ID', 'Barcode_prefix', 'Barcode_suffix', 'VALUE_DTT', 'VALUE_HRP']]

    return df_merged


def combine_assays(dfs: list[pd.DataFrame]) -> pd.DataFrame:
    """
    Combine experiment assays by ID.

    :param dfs: list of DataFrames to be mergedy by id

    :return: one merged DataFrame with activations/inhibitions only
    """
    
    new_dfs = copy.deepcopy(dfs)
    for i in range(len(new_dfs)):
        id = f"Assay {i+1} - cmpd Id"
        if '% ACTIVATION' in new_dfs[i].columns.values:
            new_dfs[i] = new_dfs[i][[id, '% ACTIVATION']]
            new_dfs[i] = new_dfs[i].rename(columns={id: 'Compound ID', '% ACTIVATION': '% ACTIVATION ' + str(i+1)})
        elif '% INHIBITION' in new_dfs[i].columns.values:
            new_dfs[i] = new_dfs[i][[id, '% INHIBITION']]
            new_dfs[i] = new_dfs[i].rename(columns={id: 'Compound ID', '% INHIBITION': '% INHIBITION ' + str(i)})
        else:
            print("raise bla bla") 

    df_merged = reduce(lambda df_left, df_right: pd.merge(df_left, df_right, 
                                              left_index=True, right_index=True, 
                                              how='outer'), new_dfs)
    df_merged = df_merged[df_merged.columns.drop(list(df_merged.filter(regex='Compound ID_')))]
    first_column = df_merged.pop('Compound ID')
    df_merged.insert(0, 'Compound ID', first_column)

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
