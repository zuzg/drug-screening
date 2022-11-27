# Put common fixtures here to be available in other test suits without explicit import

import pytest
import pandas as pd


@pytest.fixture
def dummy_fixture_return_2():
    return 2


@pytest.fixture
def experiment_df():
    df = pd.DataFrame.from_dict({
        'id': [0, 1],
        'Barcode assay plate': ['B1007L2002L03DTT1', 'B1007L2002L03DTT2'],
        'VALUE': [27269, 27290]
    })
    return df


@pytest.fixture
def combine_dataframes():
    df = pd.DataFrame.from_dict({
        'Cmpd id': [0, 1, 0],
        'Barcode assay plate': ['B1007L2002L03DTT1', 'B1007L2002L03DTT2', 'B1007L2002L03DTT4'],
        'VALUE': [27269, 27290, 2345333]
    })
    df2 = pd.DataFrame.from_dict({
        'Cmpd id': [0, 1, 2],
        'Barcode assay plate': ['B1007L2002L03DTT1', 'B1007L2002L03DTT2', 'B1007L2002L03DTT3'],
        'VALUE': [2020, 2121, 2222]
    })
    return [(df, 'Assay 1.xlsx'), (df2, 'Assay 2.xlsx')]
