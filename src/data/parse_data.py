import copy
import numpy as np
import pandas as pd
from sklearn.preprocessing import MinMaxScaler, StandardScaler, QuantileTransformer
import umap
from functools import reduce
import os
import sys
if '../' not in sys.path:
    sys.path.append('../')


def parse_data(filename: str) -> pd.DataFrame:
    """
    Basic function to parse excel file passed by filename. Drops invalid entries.

    :param str: name of the file from which data will be parsed

    :return: parsed DataFrame
    """
    df = pd.read_excel(f"../data/raw/{filename}")
    if('CONTROL OUTLIER' in df):
        del df['CONTROL OUTLIER']
    if('Transfer Status' in df and len(df[df['Transfer Status'] != 'OK']) != 0):
        print(
            f"{filename} - deleted {len(df[df['Transfer Status'] != 'OK'])} rows with invalid Transfer Status")
        df = df[df['Transfer Status'] == 'OK']
    return df


def parse_barcode(df: pd.DataFrame) -> pd.DataFrame:
    """
    Parse dataframe to extract compound's ID.

    :param df: DataFrame with barcode

    :return: DataFrame with extracted barcode prefix and suffix
    """
    new_df = df.copy(deep=True)
    new_df[['Barcode_prefix', 'Barcode_exp', 'Barcode_suffix']
           ] = new_df['Barcode assay plate'].str.extract(pat='(.{13})([^0-9]*)(.*)')

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
                         left_on=['DTT  - compound ID',
                                  'Barcode_prefix', 'Barcode_suffix'],
                         right_on=['HRP - compound ID', 'Barcode_prefix', 'Barcode_suffix'])\
        .rename(columns={'HRP - compound ID': 'Compound ID', 'VALUE_x': 'VALUE_DTT', 'VALUE_y': 'VALUE_HRP'})[['Compound ID', 'Barcode_prefix', 'Barcode_suffix', 'VALUE_DTT', 'VALUE_HRP']]

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
            new_dfs[i] = new_dfs[i].rename(
                columns={id: 'Compound ID', '% ACTIVATION': '% ACTIVATION ' + str(i+1)})
        elif '% INHIBITION' in new_dfs[i].columns.values:
            new_dfs[i] = new_dfs[i][[id, '% INHIBITION']]
            new_dfs[i] = new_dfs[i].rename(
                columns={id: 'Compound ID', '% INHIBITION': '% INHIBITION ' + str(i+1)})
        else:
            raise Exception(f"No correct column in {i+1} file")

    df_merged = reduce(lambda df_left, df_right: pd.merge(df_left, df_right,
                                                          left_index=True, right_index=True,
                                                          how='outer'), new_dfs)
    df_merged = df_merged[df_merged.columns.drop(
        list(df_merged.filter(regex='Compound ID_')))]
    first_column = df_merged.pop('Compound ID')
    df_merged.insert(0, 'Compound ID', first_column)

    return df_merged


def merge_all_assays() -> pd.DataFrame:
    d = dict()

    for file in os.listdir('../data/raw/'):
        if file.startswith('Assay'):
            d[file.replace('.xlsx', '')] = parse_data(file)
    for assay in d:
        d[assay] = d[assay].rename(str.upper, axis='columns')
    for i in range(1, 9):
        d[f'Assay {i}'] = d[f'Assay {i}'].add_suffix(f' {i}')
    for i in range(1, 4):
        d[f'Assay {i}']['ID'] = (d[f'Assay {i}'][f'ASSAY {i} - CMPD ID {i}'].astype(str) + d[f'Assay {i}']
                                 [f'BARCODE ASSAY PLATE {i}'].str[:-2]) + d[f'Assay {i}'][f'BARCODE ASSAY PLATE {i}'].str[-1]

    combined_df = pd.merge(d['Assay 1'], d['Assay 2'], on='ID')
    combined_df = pd.merge(combined_df, d['Assay 3'], on='ID')
    for i in range(4, 9):
        combined_df = pd.merge(
            combined_df, d[f'Assay {i}'], left_on='ASSAY 1 - CMPD ID 1', right_on=f'ASSAY {i} - CMPD ID {i}')
    combined_df = combined_df.rename(
        columns={'ASSAY 1 - CMPD ID 1': 'CMPD ID'})

    colnames = ['CMPD ID']
    colnames.extend([f'% ACTIVATION {i}' for i in range(1, 4)])
    colnames.extend([f'% INHIBITION {i}' for i in range(4, 9)])
    colnames.extend(['% ACTIVATION 8'])
    res = combined_df[colnames]

    return res


def normalize_columns(df: pd.DataFrame, column_names: list[str]) -> pd.DataFrame:
    """
    Function to normalize chosen columns within dataframe.

    :param df: DataFrame with columns to normalize

    :param column_names: names of columns to be normalized

    :return: DataFrame with normalized columns
    """
    scaler = StandardScaler()
    df[column_names] = scaler.fit_transform(df[column_names])

    return df


def get_umap(df: pd.DataFrame, target: str, scaler: object,
             n_neighbors=10, n_components=2, min_dist=0.2) -> np.ndarray:
    """
    Function to normalize chosen columns within dataframe.

    :param df: DataFrame with to perform UMAP

    :param target: names of column to be treated as target

    :param scaler: object with which scaling will be performed

    :return: UMAP array, target y
    """
    df_na = df.dropna(inplace=False)
    X = df_na.drop(target, axis=1)
    y = df_na[target]

    X_scaled = scaler.fit_transform(X)
    umap_transformer = umap.UMAP(
        n_neighbors=n_neighbors,
        n_components=n_components,
        min_dist=min_dist
    )
    X_umap = umap_transformer.fit_transform(X_scaled)

    return X_umap, y
