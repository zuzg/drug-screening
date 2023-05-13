import numpy as np
from unittest.mock import mock_open, patch

from src.data.bmg_plate import well_to_ids, parse_bmg_file, get_summary_tuple


def test_well_to_ids():
    well_name = "C13"
    i, j = well_to_ids(well_name)
    assert i == 2 and j == 12


def test_parse_bmg_file():
    filepath = "path/to/BMG/file/1234.txt"
    file_content = "\t28670,\t30315,\t32035,\t24320"
    with patch("builtins.open", mock_open(read_data=file_content)):
        barcode, plate = parse_bmg_file(filepath)
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
