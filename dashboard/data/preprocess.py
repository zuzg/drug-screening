from __future__ import annotations

import pandas as pd
import numpy as np

from typing import Protocol


class Projector(Protocol):
    def fit_transform(self, X: np.ndarray) -> np.ndarray:
        ...

    def transform(self, X: np.ndarray) -> np.ndarray:
        ...


class MergedAssaysPreprocessor:
    def __init__(
        self,
        raw_compounds_df: pd.DataFrame,
        columns_for_projection: list[str],
    ):
        """
        :param raw_compounds_df: compounds dataframe to be processed
        :param chemical_columns: list of names of chemical colums
        :param key_column: name of the key column, defaults to "EOS"
        """
        self.compounds_df = raw_compounds_df
        self.columns_for_projection = columns_for_projection
        self.chemical_columns = None  # TODO: incorporate chemical data

    def restrict_to_chemicals(self) -> MergedAssaysPreprocessor:
        """
        Restrict the dataframe to the chemical columns (drops all other columns)

        :return: preprocessor itself
        """
        self.compounds_df = self.compounds_df[self.chemical_columns]
        return self

    def apply_projection(
        self,
        projector: Projector,
        projection_name: str,
        just_transform: bool = False,
    ) -> MergedAssaysPreprocessor:
        """
        Apply a projection to the dataframe using a given projector

        :param projector: Projector instance
        :param projection_name: name of the projection, to be inserted in the projection columns names
        :param just_transform: whether to use just transform or fit and transform, defaults to False
        :return: preprocessor itself
        """
        X = self.compounds_df[self.columns_for_projection].to_numpy()
        if just_transform:
            X_projected = projector.transform(X)
        else:
            X_projected = projector.fit_transform(X)
        suffixes = ["X", "Y"]

        if X_projected.shape[1] > 2:
            # if more than 2 projected dimensions, use numbers as suffixes
            suffixes = range(X_projected.shape[0])
        for suffix, col in zip(suffixes, X_projected.T):
            self.compounds_df[f"{projection_name}_{suffix}"] = col
        return self

    def get_processed_df(self) -> pd.DataFrame:
        """
        Get the processed dataframe

        :return: processed dataframe
        """
        return self.compounds_df


# NOTE: to clarify
def calculate_concentration(
    df: pd.DataFrame, concetration: int, summary_assay_volume: int
) -> pd.DataFrame:
    """
    Calculate concentrations and append as column to dataframe
    :param df: dataframe to append concentration to
    :param concentration: multiplier
    :param summary_assay_volume: to divide by
    :return: dataframe
    """
    df["Concentration"] = df["Actual Volume_y"] * concetration / summary_assay_volume
    return df
