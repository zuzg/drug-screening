import pandas as pd


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
