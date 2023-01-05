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
from src.data.utils import *


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
    bar_colname = 'Barcode assay plate'
    temp = df.filter(like='BARCODE ASSAY PLATE').columns
    if len(temp != 0):
        bar_colname = temp[0]
        
    new_df = df.copy(deep=True)
    new_df[['Barcode_prefix', 'Barcode_exp', 'Barcode_suffix']] = new_df[bar_colname].str.extract(pat='(.{13})([^0-9]*)(.*)')
    return new_df


def combine_controls(dataframes: list[(pd.DataFrame, str)], agg_function = 'mean') -> pd.DataFrame:
    """
    Combine control values for given assay files.

    :param dfs: list of DataFrames and respective filenames

    :param agg_function: aggragation function to be applited on controls

    :return: one merged DataFrame
    """
    d = dict()
    res = pd.DataFrame()
    for df, name in dataframes:
        key = name.replace('.xlsx', '')
        df = df.rename(str.upper, axis='columns')
        index_col = df.filter(like='CMPD ID').columns
        assert(len(index_col) ==
               1), f"More than 1/no column(s) having 'CMPD ID' n file: {name}"

        df.rename({index_col[0]: 'CMPD ID'}, axis=1, inplace=True)
        suffix = ' - ' + key
        df = df.add_suffix(suffix)
        df.rename({'CMPD ID'+suffix: 'CMPD ID'}, axis=1, inplace=True)
        if((df['CMPD ID'] == 'CTRL NEG').any() or (df['CMPD ID'] == 'CTRL POS').any()):
            mask = (df['CMPD ID'] == 'CTRL NEG') | (df['CMPD ID'] == 'CTRL POS')
            temp = df[mask]
            temp = temp.groupby('CMPD ID').agg(agg_function, numeric_only=True)
            d[key] = temp
    
    if len(d) != 0:
        res = reduce(lambda left, right: pd.merge(left, right, on=['CMPD ID'],
                                                  how='inner'), d.values())
    res = res.reset_index(level=0)
    return res


def rename_assay_columns(df: pd.DataFrame) -> pd.DataFrame:
    """
    Rename columns with assays activation/inhibition so the assay numbers are first

    :param df: dataframe with columns to rename

    :return: dataframe with renamed columns
    """
    df_renamed = df.copy()

    for col_name in df_renamed.columns:
        if ("% ACTIVATION" in col_name or "% INHIBITION" in col_name) and "(" not in col_name:
            parts = col_name.split('-')
            new_col_name = "".join([parts[1], ' - ', parts[0]]).strip()
            df_renamed.rename(columns={col_name: new_col_name}, inplace=True)

    df_renamed.sort_index(axis=1, inplace=True)
    first_col = df_renamed.pop("CMPD ID")
    df_renamed.insert(0, "CMPD ID", first_col)
    return df_renamed


def combine_assays(dataframes: list[(pd.DataFrame, str)], barcode: bool = False, agg_function = 'max') -> pd.DataFrame:
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
        if((df['CMPD ID'] == 'CTRL NEG').any() or (df['CMPD ID'] == 'CTRL POS').any()):
            df = df.drop(df[df['CMPD ID'] == 'CTRL NEG'].index)
            df = df.drop(df[df['CMPD ID'] == 'CTRL POS'].index)

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

        res = res.groupby('CMPD ID').agg(agg_function)

    res = res.reset_index(level=0)
    if not barcode:
        res = rename_assay_columns(res)
    return res


def get_control_rows(df: pd.DataFrame) -> pd.DataFrame:
    """
    Add control rows to a DataFrame.

    :param df: DataFrame prepared i.e. with inhibition and activation columns in various assyas

    :return: DataFrame with control values
    """
    assays_cols = list(df.drop(columns=['CMPD ID']).columns)
    assays = list(x.split('-')[0].lstrip() for x in assays_cols)
    bin_seq = generate_binary_strings(len(assays))

    ctrl_df = pd.DataFrame()
    for i, seq in enumerate(bin_seq):
        neg_name_part = 'NEG: '
        pos_name_part = 'POS: '

        # it is assumed that 1 -> mean activation pos, 0 -> mean activation neg 
        for j, s in enumerate(seq):
            if s == '0':
                neg_name_part += str(assays[j]) +','
                key = list(df.filter(like=f'{assays[j]}- % ACTIVATION').columns)
                if len(key) != 0:
                    ctrl_df.loc[i, key[0]] = 0
                key = list(df.filter(like=f'{assays[j]}- % INHIBITION').columns)
                if len(key) != 0:
                    ctrl_df.loc[i, key[0]] = 100
            else:
                pos_name_part += str(assays[j]) +','
                key = list(df.filter(like=f'{assays[j]}- % ACTIVATION').columns)
                if len(key) != 0:
                    ctrl_df.loc[i, key[0]] = 100
                key = list(df.filter(like=f'{assays[j]}- % INHIBITION').columns)
                if len(key) != 0:
                    ctrl_df.loc[i, key[0]] = 0
        if pos_name_part[-1]==',':
            pos_name_part = pos_name_part[:-1]
        if neg_name_part[-1]==',':
            neg_name_part = neg_name_part[:-1]

        name = pos_name_part + ';' + neg_name_part
        ctrl_df.loc[i, 'CMPD ID'] = name
    return ctrl_df


def split_compounds_controls(df: pd.DataFrame) -> tuple[pd.DataFrame, pd.DataFrame]:
    """
    Splits a DataFrame into two with only compounds and control values respectively.

    :param df: DataFrame with control values added.

    :return: two data frames with only compounds and only control values.
    """
    mask = df['CMPD ID'].str.startswith('POS', na = False)
    return df[~mask], df[mask]


def split_controls_pos_neg(df: pd.DataFrame, column_name: str) -> dict[pd.DataFrame]:
    """
    Splits a DataFrame into a dictionary of different categories of positive and negative controls with respect to yhe pre-defined assay.

    :param df: DataFrame with control values.

    :param column_name: Column name with assay suffix.

    :return: Dictionary of positive and negative controls.
    """
    assay_name = column_name.split('-')[-1][1:]
    controls_categorized = dict()
    dict_keys = ['all_pos', 'all_but_one_pos', 'pos', 'all_neg', 'all_but_one_neg', 'neg']

    for k in dict_keys:
        controls_categorized[k] = pd.DataFrame(columns=df.columns)
    
    pos = list()
    neg = list()
    for index, row in df.iterrows():
        cmpd_id = row['CMPD ID']
        # example: POS:Assay 5;NEG:Assay 2
        cmpd_id = cmpd_id.split(';')
        if cmpd_id[1] == 'NEG: ' and assay_name in cmpd_id[0]:
                controls_categorized['all_pos'] = pd.concat([controls_categorized['all_pos'], pd.DataFrame(row).T])
            
        elif cmpd_id[0] == 'POS: ' and assay_name in cmpd_id[1]:
                controls_categorized['all_neg'] = pd.concat([controls_categorized['all_neg'], pd.DataFrame(row).T])

        else:
            assay_pos = cmpd_id[0][5:].split(',')
            assay_neg = cmpd_id[1][5:].split(',')

            if assay_name in assay_pos:
                if len(assay_neg) == 1:
                    controls_categorized['all_but_one_pos'] = pd.concat([controls_categorized['all_but_one_pos'], pd.DataFrame(row).T])
                else:
                    controls_categorized['pos'] = pd.concat([controls_categorized['pos'], pd.DataFrame(row).T])

            elif assay_name in assay_neg:
                if len(assay_pos) == 1:
                    controls_categorized['all_but_one_neg'] = pd.concat([controls_categorized['all_but_one_neg'], pd.DataFrame(row).T])
                else:
                    controls_categorized['neg'] = pd.concat([controls_categorized['neg'], pd.DataFrame(row).T])

    return controls_categorized


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


def get_umap(df: pd.DataFrame, controls: pd.DataFrame, target: str, scaler: object,
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
    controls_na = controls.dropna(inplace=False)
    X_ctrl = controls_na.drop(target, axis=1)
    if scaler:
        X = scaler.fit_transform(X)
        X_ctrl = scaler.fit_transform(X_ctrl)
    umap_transformer = umap.UMAP(
        n_neighbors=n_neighbors,
        n_components=n_components,
        min_dist=min_dist,
        random_state=23
    )
    X_umap = umap_transformer.fit_transform(X)
    X_ctrl = umap_transformer.transform(X_ctrl)

    return X_umap, X_ctrl


def get_pca(df: pd.DataFrame, controls: pd.DataFrame, target: str, scaler: object, n_components=2) -> np.ndarray:
    """
    Get PCA projection for given dataframe.

    :param df: DataFrame with to perform PCA

    :param target: names of column to be treated as target

    :param scaler: object with which scaling will be performed

    :return: PCA array
    """
    df_na = df.dropna(inplace=False)
    X = df_na.drop(target, axis=1)
    controls_na = controls.dropna(inplace=False)
    X_ctrl = controls_na.drop(target, axis=1)
    if scaler:
        X = scaler.fit_transform(X)
        X_ctrl = scaler.fit_transform(X_ctrl)
    pca = PCA(n_components=n_components)
    X_pca = pca.fit_transform(X)
    X_ctrl = pca.transform(X_ctrl)

    return X_pca, X_ctrl


def get_tsne(df: pd.DataFrame, target: str, scaler: object, n_components=2,
             learning_rate='auto', init='random', perplexity=3) -> np.ndarray:
    """
    Get t-SNE projection for given dataframe.

    :param df: DataFrame with to perform t-SNE

    :param target: names of column to be treated as target

    :param scaler: object with which scaling will be performed

    :return: t-SNE array
    """
    df_na = df.dropna(inplace=False)
    X = df_na.drop(target, axis=1)
    if scaler:
        X = scaler.fit_transform(X)
    tsne = TSNE(n_components=n_components,
                learning_rate=learning_rate, init=init, perplexity=perplexity)
    
    X_tsne = tsne.fit_transform(X)

    return X_tsne


def get_projections(df: pd.DataFrame, controls: pd.DataFrame) -> pd.DataFrame:
    """
    Add columns with projected values to exisisting dataframe

    :param df: DataFrame to peform projections

    :param get_3d: if True it returns also the third dimension

    :return: dataframe with added projection columns
    """
    df_umap, controls_umap = get_umap(df, controls, 'CMPD ID', scaler=False)
    df_pca, controls_pca = get_pca(df, controls, 'CMPD ID', scaler=False)
    points_all = pd.concat([df, controls])
    df_tsne_all = get_tsne(points_all, 'CMPD ID', scaler=False)

    # CMPD ID
    df_expanded = df.copy()
    df_expanded['UMAP_X'] = df_umap[:, 0]
    df_expanded['UMAP_Y'] = df_umap[:, 1]
    df_expanded['PCA_X'] = df_pca[:, 0]
    df_expanded['PCA_Y'] = df_pca[:, 1]
    points_all['TSNE_X'] = df_tsne_all[:, 0]
    points_all['TSNE_Y'] = df_tsne_all[:, 1]
    df_tsne, controls_tsne = split_compounds_controls(points_all)
    df_expanded['TSNE_X'] = df_tsne['TSNE_X']
    df_expanded['TSNE_Y'] = df_tsne['TSNE_Y']

    # CONTROLS
    controls_expanded = controls.copy()
    controls_expanded['UMAP_X'] = controls_umap[:, 0]
    controls_expanded['UMAP_Y'] = controls_umap[:, 1]
    controls_expanded['PCA_X'] = controls_pca[:, 0]
    controls_expanded['PCA_Y'] = controls_pca[:, 1]
    controls_expanded['TSNE_X'] = controls_tsne['TSNE_X']
    controls_expanded['TSNE_Y'] = controls_tsne['TSNE_Y']

    return df_expanded, controls_expanded


def add_ecbd_links(df: pd.DataFrame) -> pd.DataFrame:
    """
    Mock connection with European Chemical Biology Database - add link to the compound page

    :param df: DataFrame to add links

    :return: dataframe with added EOS columns
    """
    eos = [f"[EOS{i}](https://ecbd.eu/compound/EOS{i})" for i in range(1, len(df)+1)]
    new_df = df.copy()
    new_df.insert(1, "EOS", eos)

    return new_df
