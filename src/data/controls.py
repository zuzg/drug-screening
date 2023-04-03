import itertools

import numpy as np
import pandas as pd

from typing import Any


def controls_index_annotator(index: Any) -> str:
    """
    Annotate control index.

    :param index: index value to annotate
    :return: control annotation
    """
    index_as_str = str(index)
    num_assays = index_as_str.count("Assay")
    if not num_assays:
        return "NOT CONTROL"
    pos, neg = index_as_str.split(";")
    pos_assays = pos.count("Assay")
    neg_assays = num_assays - pos_assays
    if not pos_assays:
        return "ALL NEGATIVE"
    if not neg_assays:
        return "ALL POSITIVE"
    if pos_assays == 1 and neg_assays != 1:
        return "ALL BUT ONE NEGATIVE"
    if pos_assays != 1 and neg_assays == 1:
        return "ALL BUT ONE POSITIVE"
    if pos_assays >= neg_assays:
        return "MORE POSITIVE"
    return "MORE NEGATIVE"


def create_control_id(values: np.ndarray, columns: list[str]) -> str:
    """
    Creates a control ID based on the values of the control and the assay columns.
    :param values: Array of values for the control.
    :param columns: List of assay columns.
    :return: Control ID.
    """
    positive = "POS: " + ", ".join(
        column for i, column in enumerate(columns) if values[i]
    )
    negative = "NEG: " + ", ".join(
        column for i, column in enumerate(columns) if not values[i]
    )

    return f"{positive}; {negative}"


def generate_controls(columns: list[str], key_column: str = "CMPD ID") -> pd.DataFrame:
    """
    Generate control data for a given set of columns with all possible positive/negative activations.
    For inhibition values are inverted.
    :param columns: list of chemical assay columns
    :param key_column: name of the ID column, defaults to "CMPD ID"
    :return: dataframe with control data
    """
    sequences = list(itertools.product([0, 1], repeat=len(columns)))
    control_data = np.array(sequences)
    is_activation = np.array(["ACTIVATION" in col for col in columns])
    column_prefixes = [col.split("-")[0].strip() for col in columns]
    control_index = [create_control_id(row, column_prefixes) for row in control_data]
    control_data[:, ~is_activation] ^= 1
    control_data = control_data * 100
    control_data = pd.DataFrame(
        control_data, columns=columns, index=range(len(sequences))
    )
    control_data[key_column] = control_index
    return control_data
