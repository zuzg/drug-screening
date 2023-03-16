import itertools

import pandas as pd


def generate_binary_strings(bit_count: int) -> list[str]:
    return ["".join(num_bin) for num_bin in itertools.product("01", repeat=bit_count)]


def generate_control_values_dataframe() -> pd.DataFrame:
    ...


def generate_dummy_links_dataframe(compound_ids: list[str]) -> pd.DataFrame:
    eos = [
        f"[EOS{i+1}](https://ecbd.eu/compound/EOS{i+1})"
        for i, _ in enumerate(compound_ids)
    ]
    return pd.DataFrame({"CMPD ID": compound_ids, "EOS": eos}).set_index("CMPD ID")


def is_chemical_result(column_name: str) -> bool:
    """
    Check if column name is a chemical result one
    :param column_name: column_name to check
    :return: Whether the column contains chemical results or not
    """
    return (
        "% ACTIVATION" in column_name or "% INHIBITION" in column_name
    ) and "(" not in column_name


def get_chemical_columns(columns: list[str]) -> list[str]:
    return [column for column in columns if is_chemical_result(column)]

def split_controls_pos_neg(df: pd.DataFrame, column_name: str) -> dict[pd.DataFrame]:
    """
    Splits a DataFrame into a dictionary of different categories of positive and negative controls with respect to yhe pre-defined assay.

    :param df: DataFrame with control values.

    :param column_name: Column name with assay suffix.

    :return: Dictionary of positive and negative controls.
    """
    assay_name = column_name.split('-')[0].strip()
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