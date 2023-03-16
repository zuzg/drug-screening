import pandas as pd


from src.data.utils import generate_binary_strings


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


def get_control_rows(df: pd.DataFrame) -> pd.DataFrame:
    """
    Add control rows to a DataFrame.

    :param df: DataFrame prepared i.e. with inhibition and activation columns in various assays
    :return: DataFrame with control values
    """
    assays_cols = list(df.drop(columns=["CMPD ID"]).columns)
    assays = sorted({x.split("-")[0].strip() for x in assays_cols})
    bin_seq = generate_binary_strings(len(assays))

    ctrl_df = pd.DataFrame()
    for i, seq in enumerate(bin_seq):
        neg_name_part = "NEG: "
        pos_name_part = "POS: "

        # it is assumed that 1 -> mean activation pos, 0 -> mean activation neg
        for j, s in enumerate(seq):
            if s == "0":
                neg_name_part += str(assays[j]) + ","
                key = list(df.filter(like=f"{assays[j]} - % ACTIVATION").columns)
                if len(key) != 0:
                    ctrl_df.loc[i, key[0]] = 0
                key = list(df.filter(like=f"{assays[j]} - % INHIBITION").columns)
                if len(key) != 0:
                    ctrl_df.loc[i, key[0]] = 100
            else:
                pos_name_part += str(assays[j]) + ","
                key = list(df.filter(like=f"{assays[j]} - % ACTIVATION").columns)
                if len(key) != 0:
                    ctrl_df.loc[i, key[0]] = 100
                key = list(df.filter(like=f"{assays[j]} - % INHIBITION").columns)
                if len(key) != 0:
                    ctrl_df.loc[i, key[0]] = 0
        if pos_name_part[-1] == ",":
            pos_name_part = pos_name_part[:-1]
        if neg_name_part[-1] == ",":
            neg_name_part = neg_name_part[:-1]

        name = pos_name_part + ";" + neg_name_part
        ctrl_df.loc[i, "CMPD ID"] = name
    return ctrl_df


def split_compounds_controls(df: pd.DataFrame) -> tuple[pd.DataFrame, pd.DataFrame]:
    """
    Splits a DataFrame into two with only compounds and control values respectively.

    :param df: DataFrame with control values added.

    :return: two data frames with only compounds and only control values.
    """
    mask = df["CMPD ID"].str.startswith("POS", na=False)
    return df[~mask], df[mask]


def split_controls_pos_neg(df: pd.DataFrame, column_name: str) -> dict[pd.DataFrame]:
    """
    Splits a DataFrame into a dictionary of different categories of positive and negative controls with respect to yhe pre-defined assay.

    :param df: DataFrame with control values.

    :param column_name: Column name with assay suffix.

    :return: Dictionary of positive and negative controls.
    """
    assay_name = column_name.split("-")[0].strip()
    dict_keys = [
        "all_pos",
        "all_but_one_pos",
        "pos",
        "all_neg",
        "all_but_one_neg",
        "neg",
    ]
    controls_categorized = {key: pd.DataFrame(columns=df.columns) for key in dict_keys}
    for index, row in df.iterrows():
        cmpd_id = row["CMPD ID"]
        # example: POS:Assay 5;NEG:Assay 2
        cmpd_id = cmpd_id.split(";")
        if cmpd_id[1] == "NEG: " and assay_name in cmpd_id[0]:
            controls_categorized["all_pos"] = pd.concat(
                [controls_categorized["all_pos"], pd.DataFrame(row).T]
            )

        elif cmpd_id[0] == "POS: " and assay_name in cmpd_id[1]:
            controls_categorized["all_neg"] = pd.concat(
                [controls_categorized["all_neg"], pd.DataFrame(row).T]
            )

        else:
            assay_pos = cmpd_id[0][5:].split(",")
            assay_neg = cmpd_id[1][5:].split(",")

            if assay_name in assay_pos:
                if len(assay_neg) == 1:
                    controls_categorized["all_but_one_pos"] = pd.concat(
                        [controls_categorized["all_but_one_pos"], pd.DataFrame(row).T]
                    )
                else:
                    controls_categorized["pos"] = pd.concat(
                        [controls_categorized["pos"], pd.DataFrame(row).T]
                    )

            elif assay_name in assay_neg:
                if len(assay_pos) == 1:
                    controls_categorized["all_but_one_neg"] = pd.concat(
                        [controls_categorized["all_but_one_neg"], pd.DataFrame(row).T]
                    )
                else:
                    controls_categorized["neg"] = pd.concat(
                        [controls_categorized["neg"], pd.DataFrame(row).T]
                    )

    return controls_categorized


def get_activation_inhibition(df: pd.DataFrame) -> pd.DataFrame:
    """
    Helper function to filter only activation and inhibition values.

    :param df: DataFrame with to be filtered

    :return: filtered dataframe
    """
    new_df = df.copy()
    columns = ["CMPD ID"]
    columns.extend(list(new_df.filter(like="- % ACTIVATION").columns))
    columns.extend(list(new_df.filter(like="- % INHIBITION").columns))
    new_df = new_df[columns]
    new_df.dropna(inplace=True)

    return new_df
