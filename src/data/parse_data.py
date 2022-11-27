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
    bar_colname = 'Barcode assay plate'
    temp = df.filter(like='BARCODE ASSAY PLATE').columns
    if len(temp != 0):
        bar_colname = temp[0]
        
    new_df = df.copy(deep=True)
    new_df[['Barcode_prefix', 'Barcode_exp', 'Barcode_suffix']] = new_df[bar_colname].str.extract(pat='(.{13})([^0-9]*)(.*)')
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
        df =  df.rename(str.upper, axis='columns')
        index_col = df.filter(like='CMPD ID').columns
        assert(len(index_col) == 1), f"More than 1/no column(s) having 'CMPD ID' n file: {name}"
        
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

        res = reduce(lambda  left,right: pd.merge(left,right,on=['ID'],
                                                how='outer'), bar_df)
        

        bar_cols = res.filter(like='Barcode_').columns
        res.drop(bar_cols, axis=1, inplace=True)

    else:
        res = reduce(lambda  left,right: pd.merge(left,right,on=['CMPD ID'],
                                                how='outer'), d.values())
        
        res = res.groupby('CMPD ID').agg('max')

    return res



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
