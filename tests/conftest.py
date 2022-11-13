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
