from src.data.parse_data import *


def test_parse_barcode(experiment_df):
    new_df = parse_barcode(experiment_df)
    assert new_df['Barcode_prefix'][0] == 'B1007L2002L03'


def test_combining_experiments():
    # TODO add this test after generalizing combining experiments
    assert True


def test_column_normalization(experiment_df):
    normalized = normalize_columns(experiment_df, ['VALUE'])
    X = experiment_df['VALUE']
    X_std = (X - X.min(axis=0)) / (X.max(axis=0) - X.min(axis=0))
    X_scaled = X_std * (X.max() - X.min()) + X.min()
    assert normalized['VALUE'][0] == X_scaled[0]
