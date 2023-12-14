from __future__ import annotations

import io
from functools import reduce
from typing import Protocol, Callable, Any

import numpy as np
import pandas as pd


class Projector(Protocol):
    def fit_transform(self, X: np.ndarray) -> np.ndarray:
        ...

    def transform(self, X: np.ndarray) -> np.ndarray:
        ...


class MergedAssaysPreprocessor:
    def __init__(
        self,
    ):
        """
        Parser for csv projection files.
        """
        self.compounds_df = None
        self.controls_df = None
        self.columns_for_projection = None

    def combine_assays_for_projections(
        self, projection_files: tuple[str, io.StringIO], id_column: str = "EOS"
    ) -> MergedAssaysPreprocessor:
        processed_dfs = []
        COLUMNS_TO_DROP = [
            "Source Plate Barcode",
            "Source Well",
            "Destination Plate Barcode",
            "Destination Well",
            "Actual Volume",
        ]

        for filename, filecontent in projection_files:
            df = pd.read_csv(filecontent, index_col=[0]).drop(columns=COLUMNS_TO_DROP)
            processed_df = df.groupby(id_column).mean()
            processed_df = processed_df.rename(
                columns={
                    "% ACTIVATION": f"% ACTIVATION {filename}",
                    "% INHIBITION": f"%INHIBITION {filename}",
                    "Z-SCORE": f"Z-SCORE {filename}",
                }
            )
            processed_dfs.append(processed_df)

        self.compounds_df = reduce(
            lambda left, right: pd.merge(left, right, on=id_column, how="inner"),
            processed_dfs,
        )
        return self

    def set_compounds_df(self, compounds_df: pd.DataFrame) -> MergedAssaysPreprocessor:
        """
        Set the compounds dataframe

        :param compounds_df: compounds dataframe
        :return: preprocessor itself
        """
        self.compounds_df = compounds_df
        return self

    def set_controls_df(self, controls_df: pd.DataFrame) -> MergedAssaysPreprocessor:
        """
        Set the controls dataframe

        :param controls_df: controls dataframe
        :return: preprocessor itself
        """
        self.controls_df = controls_df
        return self

    def set_columns_for_projection(
        self, columns_for_projection: list[str]
    ) -> MergedAssaysPreprocessor:
        """
        Set the columns for projection based on a key

        :param key: key to search for in the column names
        :return: preprocessor itself
        """
        self.columns_for_projection = columns_for_projection
        return self

    def annotate_controls(
        self, annotator: Callable[[Any], str]
    ) -> MergedAssaysPreprocessor:
        """
        Annotates the dataframe by a given annotator function

        :param annotator: function to annotate the dataframe
        :return: preprocessor itself
        """
        self.controls_df.set_index("EOS", inplace=True)
        self.controls_df["annotation"] = self.controls_df.index.map(annotator)
        self.controls_df.reset_index(inplace=True)
        return self

    def apply_projection(
        self,
        projector: Projector,
        projection_name: str,
    ) -> MergedAssaysPreprocessor:
        """
        Apply a projection to the dataframe using a given projector

        :param projector: Projector instance
        :param projection_name: name of the projection, to be inserted in the projection columns names
        :return: preprocessor itself
        """

        X = self.compounds_df[self.columns_for_projection].to_numpy()
        X_projected = projector.fit_transform(X)

        X_controls = self.controls_df[self.columns_for_projection].to_numpy()
        X_projected_controls = projector.transform(X_controls)

        suffixes = ["X", "Y", "Z"]

        if X_projected.shape[1] > len(suffixes):
            # if more than 2 projected dimensions, use numbers as suffixes
            suffixes = range(X_projected.shape[0])

        for suffix, col in zip(suffixes, X_projected.T):
            self.compounds_df[f"{projection_name}_{suffix}"] = col
        for suffix, col in zip(suffixes, X_projected_controls.T):
            self.controls_df[f"{projection_name}_{suffix}"] = col
        return self

    def get_processed_compounds_df(self) -> pd.DataFrame:
        """
        Get the processed dataframe

        :return: processed dataframe
        """
        return self.compounds_df

    def get_processed_controls_df(self) -> pd.DataFrame:
        """
        Get the processed controls dataframe

        :return: processed controls dataframe
        """
        return self.controls_df


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
    df["Concentration"] = df["Actual Volume_1"] * concetration / summary_assay_volume
    return df
