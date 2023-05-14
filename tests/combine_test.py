import numpy as np
import pandas as pd
from src.data.combine import (
    values_array_to_column,
    get_activation_inhibition_zscore_df,
    split_compounds_controls,
    combine_bmg_echo_data,
)


def test_values_array_to_column():
    values = np.array([[1.0, 2.0], [3.0, 4.0]])
    outliers = np.array([[0, 1], [1, 0]])

    result = values_array_to_column(values, outliers, "TestColumn")

    expected_result = pd.DataFrame({"Well": ["A01", "B02"], "TestColumn": [1.0, 4.0]})
    assert result.equals(expected_result)


def test_get_activation_inhibition_zscore_df(values_dict):
    result = get_activation_inhibition_zscore_df("1234", values_dict)
    expected_result = pd.DataFrame(
        {
            "Well": ["A01", "A02", "B02"],
            "% ACTIVATION": [1.0, 2.0, 4.0],
            "% INHIBITION": [0.5, 0.2, 0.3],
            "Z-SCORE": [-1.0, 0.5, -0.5],
            "Barcode": ["1234", "1234", "1234"],
        }
    )
    assert result.equals(expected_result)


def test_split_compounds_controls():
    df = pd.DataFrame(
        {
            "Destination Well": ["A01", "A02", "B01", "B02", "C23", "C24"],
            "Value": [1.0, 2.0, 3.0, 4.0, 0.5, 0.3],
        }
    )

    compounds_df, control_pos_df, control_neg_df = split_compounds_controls(df)

    expected_compounds_df = pd.DataFrame(
        {
            "Destination Well": ["A01", "A02", "B01", "B02"],
            "Value": [1.0, 2.0, 3.0, 4.0],
        }
    )

    assert expected_compounds_df.equals(compounds_df)
    assert control_pos_df.iloc[0]["Value"] == 0.3
    assert control_neg_df.iloc[0]["Value"] == 0.5


def test_combine_bmg_echo_data(df_stats):
    echo_data = {
        "Destination Plate Barcode": ["1234"] * 96,
        "Destination Well": [
            f"{chr(i // 24 + 65)}{(i % 24) + 1:02d}" for i in range(96)
        ],
        "Volume": [100] * 96,
        "Value": [i // 8 + 1 for i in range(96)],
    }
    echo_df = pd.DataFrame.from_dict(echo_data)
    plate_values = np.random.rand(1, 2, 16, 24)
    modes = {"1234": "activation"}
    combined_df = combine_bmg_echo_data(echo_df, df_stats, plate_values, modes)

    assert len(combined_df) == 96
    assert set(combined_df.columns) == set(echo_data.keys()) | {
        "% ACTIVATION",
        "Z-SCORE",
    }
    assert sorted(list(combined_df.columns)) == sorted(
        [
            "Destination Plate Barcode",
            "Destination Well",
            "Volume",
            "Value",
            "% ACTIVATION",
            "Z-SCORE",
        ]
    )
