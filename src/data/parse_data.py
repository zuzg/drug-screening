import copy
import numpy as np
import pandas as pd
from sklearn.preprocessing import StandardScaler
from sklearn.decomposition import PCA
from sklearn.manifold import TSNE
import umap
from functools import reduce
import os
import sys
if '../' not in sys.path:
    sys.path.append('../')
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
    if('Transfer Status' in df and len(df[df['Transfer Status'] != 'OK']) != 0):
        print(
            f"{filename} - deleted {len(df[df['Transfer Status'] != 'OK'])} rows with invalid Transfer Status")
        df = df[df['Transfer Status'] == 'OK']
    return df


def combine_assays(dataframes: list[(pd.DataFrame, str)], barcode: bool = False) -> pd.DataFrame:
    """
    Combine assays by compound ID.

    :param dfs: list of DataFrames and respective filenames

    :param barcode: value indicating checking upon the barcode

    :return: one merged DataFrame
    """
    d = dict()
    barcode_files = list()
    non_barcode_files = list()
    res = pd.DataFrame()

    for df, name in dataframes:
        key = name.replace('.xlsx', '')
        df = df.rename(str.upper, axis='columns')
        index_col = df.filter(like='CMPD ID').columns
        assert(len(index_col) ==
               1), f"More than 1/no column(s) having 'CMPD ID' n file: {name}"

        df.rename({index_col[0]: 'CMPD ID'}, axis=1, inplace=True)

        # check upon the barcode
        if barcode:
            df2 = parse_barcode(df)
            if(set(df2['Barcode_suffix'].values) != {''}):
                barcode_files.append(key)
                df = df2
            else:
                non_barcode_files.append(key)

        suffix = ' - ' + key
        df = df.add_suffix(suffix)
        df.rename({'CMPD ID'+suffix: 'CMPD ID'}, axis=1, inplace=True)
        d[key] = df

    # create ID column for the assays containing barcode suffix
    if barcode and len(barcode_files) != 0:
        for bar_file in barcode_files:
            d[bar_file]['ID'] = (d[bar_file][f'CMPD ID'].astype(str) +
                                 d[bar_file][f'Barcode_prefix - {bar_file}']) + d[bar_file][f'Barcode_suffix - {bar_file}']

        bar_df = [d[b] for b in barcode_files]

        res = reduce(lambda left, right: pd.merge(left, right, on=['ID'],
                                                  how='outer'), bar_df)

        bar_cols = res.filter(like='Barcode_').columns
        res.drop(bar_cols, axis=1, inplace=True)

    else:
        res = reduce(lambda left, right: pd.merge(left, right, on=['CMPD ID'],
                                                  how='outer'), d.values())

        res = res.groupby('CMPD ID').agg('max')

    res = res.reset_index(level=0)
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


def get_activation_inhibition(df: pd.DataFrame) -> pd.DataFrame:
    """
    Helper function to filter only activation and inhibition values.

    :param df: DataFrame with to be filtered

    :return: filtered dataframe
    """
    new_df = df.copy()
    columns = ['CMPD ID']
    columns.extend(list(new_df.filter(like='% ACTIVATION - ').columns))
    columns.extend(list(new_df.filter(like='% INHIBITION - ').columns))
    new_df = new_df[columns]
    new_df.dropna(inplace=True)

    return new_df


def get_umap(df: pd.DataFrame, target: str, scaler: object,
             n_neighbors=10, n_components=2, min_dist=0.2) -> np.ndarray:
    """
    Get UMAP projection for given dataframe.

    :param df: DataFrame with to perform UMAP

    :param target: names of column to be treated as target

    :param scaler: object with which scaling will be performed

    :return: UMAP array
    """
    df_na = df.dropna(inplace=False)
    X = df_na.drop(target, axis=1)
    if scaler:
        X = scaler.fit_transform(X)
    umap_transformer = umap.UMAP(
        n_neighbors=n_neighbors,
        n_components=n_components,
        min_dist=min_dist
    )
    X_umap = umap_transformer.fit_transform(X)

    return X_umap


def get_pca(df: pd.DataFrame, target: str, scaler: object, n_components=2) -> np.ndarray:
    """
    Get PCA projection for given dataframe.

    :param df: DataFrame with to perform PCA

    :param target: names of column to be treated as target

    :param scaler: object with which scaling will be performed

    :return: PCA array
    """
    X = df.drop(target, axis=1)
    if scaler:
        X = scaler.fit_transform(X)
    pca = PCA(n_components=n_components)
    X_pca = pca.fit_transform(X)

    return X_pca


def get_tsne(df: pd.DataFrame, target: str, scaler: object, n_components=2,
             learning_rate='auto', init='random', perplexity=3) -> np.ndarray:
    """
    Get t-SNE projection for given dataframe.

    :param df: DataFrame with to perform t-SNE

    :param target: names of column to be treated as target

    :param scaler: object with which scaling will be performed

    :return: t-SNE array
    """
    X = df.drop(target, axis=1)
    if scaler:
        X = scaler.fit_transform(X)
    tsne = TSNE(n_components=n_components,
                learning_rate=learning_rate, init=init, perplexity=perplexity)
    X_tsne = tsne.fit_transform(X)

    return X_tsne


def get_projections(df: pd.DataFrame) -> pd.DataFrame:
    """
    Add columns with projected values to exisisting dataframe

    :param df: DataFrame to peform projections

    :return: dataframe with added projection columns
    """
    df_umap = get_umap(df, 'CMPD ID', scaler=False)
    df_pca = get_pca(df, 'CMPD ID', scaler=False)
    df_tsne = get_tsne(df, 'CMPD ID', scaler=False)
    df_expanded = df.copy()

    df_expanded['UMAP_X'] = df_umap[:, 0]
    df_expanded['UMAP_Y'] = df_umap[:, 1]
    df_expanded['PCA_X'] = df_pca[:, 0]
    df_expanded['PCA_Y'] = df_pca[:, 1]
    df_expanded['tSNE_X'] = df_tsne[:, 0]
    df_expanded['tSNE_Y'] = df_tsne[:, 1]

    return df_expanded
