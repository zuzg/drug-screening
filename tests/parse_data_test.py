from src.data.combine import combine_assays
from src.data.parse import *
from src.data.preprocess import normalize_columns


def test_combining_experiments():
    # TODO add this test after generalizing combining experiments
    assert True


def test_combine_experiments(combine_dataframes):
    merged_df = combine_assays(combine_dataframes)
    assert merged_df["VALUE - Assay 1"][0] == 2345333


def test_combine_experiments_barcode(combine_dataframes):
    merged_df = combine_assays(combine_dataframes, barcode=True)
    assert merged_df["VALUE - Assay 1"].isna().sum() == 1


def test_column_normalization(experiment_df):
    normalized = normalize_columns(experiment_df, ["VALUE"])
    X = experiment_df["VALUE"]
    X_std = (X - X.min(axis=0)) / (X.max(axis=0) - X.min(axis=0))
    X_scaled = X_std * (X.max() - X.min()) + X.min()
    assert normalized["VALUE"][0] == X_scaled[0]
