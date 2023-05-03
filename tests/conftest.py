# Put common fixtures here to be available in other test suits without explicit import

import pytest
import numpy as np
import pandas as pd
from src.data.bmg_plate import Plate, get_summary_tuple


@pytest.fixture
def experiment_df():
    df = pd.DataFrame.from_dict(
        {
            "id": [0, 1],
            "Barcode assay plate": ["B1007L2002L03DTT1", "B1007L2002L03DTT2"],
            "VALUE": [27269, 27290],
        }
    )
    return df


@pytest.fixture
def combine_dataframes():
    df = pd.DataFrame.from_dict(
        {
            "Cmpd id": [0, 1, 0],
            "Barcode assay plate": [
                "B1007L2002L03DTT1",
                "B1007L2002L03DTT2",
                "B1007L2002L03DTT4",
            ],
            "VALUE": [27269, 27290, 2345333],
        }
    )
    df2 = pd.DataFrame.from_dict(
        {
            "Cmpd id": [0, 1, 2],
            "Barcode assay plate": [
                "B1007L2002L03DTT1",
                "B1007L2002L03DTT2",
                "B1007L2002L03DTT3",
            ],
            "VALUE": [2020, 2121, 2222],
        }
    )
    return [df, df2]


@pytest.fixture
def plate_summary():
    barcode = "abcd"
    plate_array = np.array([[1, 3, 2], [0, 0, 0]])
    plate = Plate(barcode, plate_array)
    summary = get_summary_tuple(plate)
    return summary
