from unittest.mock import mock_open, patch

import numpy as np
import pandas as pd

from dashboard.data.bmg_plate import (
    calculate_activation_inhibition_zscore,
    filter_low_quality_plates,
    get_activation_inhibition_zscore_dict,
    parse_bmg_file,
    well_to_ids,
)


def test_well_to_ids():
    well_name = "C13"
    i, j = well_to_ids(well_name)
    assert i == 2 and j == 12


def test_parse_bmg_file():
    filename = "1234.txt"
    file_content = "\t28670,\t30315,\t32035,\t24320"
    with patch("builtins.open", mock_open(read_data=file_content)):
        barcode, plate = parse_bmg_file(filename, file_content)
        assert barcode == "1234" and plate[0, 0] == 28670


def test_plate_class(plate_summary):
    errors = []
    if plate_summary.std_neg != 1.5:
        errors.append("std_pos error")
    if plate_summary.std_pos != 1:
        errors.append("std_neg error")
    if plate_summary.mean_neg != 1.5:
        errors.append("mean_pos error")
    if plate_summary.mean_pos != 1:
        errors.append("mean_neg error")
    if plate_summary.z_factor != -14:
        errors.append("z_factor error")
    assert not errors


def test_outliers(plate_summary):
    assert plate_summary.z_factor == plate_summary.z_factor_no_outliers


def test_calculate_activation_inhibition_zscore(stats_for_all):
    values = np.array([5, 3, 3])

    activation, inhibition, z_score = calculate_activation_inhibition_zscore(
        values, stats_for_all, "activation", False
    )
    assert (
        round(activation[2], 2) == -199.25
        and round(z_score[0], 2) == -82.92
        and inhibition is None
    )


def test_get_activation_inhibition_zscore_dict(df_stats):
    values = np.full((2, 2, 16, 24), 2)
    values[1] = 1.5
    z_dict = get_activation_inhibition_zscore_dict(df_stats, values, "activation")
    assert np.array_equal(z_dict["1234"]["z_score"], np.full((16, 24), 1.0))


def test_filter_low_quality_plates(df_stats):
    values = np.array([[5, 3, 3], [0, 1, 0]])
    (
        quality_df,
        _,
        quality_plates,
    ) = filter_low_quality_plates(df_stats, values, -2.5)
    df_diff = pd.concat([df_stats, quality_df]).drop_duplicates(keep=False)
    assert df_diff.empty and np.array_equal(quality_plates, values)
