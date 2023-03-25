from __future__ import annotations

import pandas as pd
import numpy as np

from typing import Protocol, Callable, Any


class Projector(Protocol):
    def fit_transform(self, X: np.ndarray) -> np.ndarray:
        ...

    def transform(self, X: np.ndarray) -> np.ndarray:
        ...


class MergedAssaysPreprocessor:
    def __init__(
        self,
        raw_compounds_df: pd.DataFrame,
        chemical_columns: list[str],
        key_column: str = "CMPD ID",
    ):
        """
        :param raw_compounds_df: compounds dataframe to be processed
        :param chemical_columns: list of names of chemical colums
        :param key_column: name of the key column, defaults to "CMPD ID"
        """
        self.chemical_columns = chemical_columns
        self.compounds_df = raw_compounds_df.set_index(key_column)

    def restrict_to_chemicals(self) -> MergedAssaysPreprocessor:
        """
        Restrict the dataframe to the chemical columns (drops all other columns)

        :return: preprocessor itself
        """
        self.compounds_df = self.compounds_df[self.chemical_columns]
        return self

    def group_duplicates_by_function(self, func_name: str) -> MergedAssaysPreprocessor:
        """
        Group duplicates by a function (e.g. mean, median, max, min, etc.)

        :param func_name: name of the function to use
        :return: preprocessor itself
        """
        self.compounds_df = self.compounds_df.groupby(level=0).agg(func_name)
        return self

    def drop_na(self) -> MergedAssaysPreprocessor:
        """
        Drops duplicates in the dataframe.

        :return: preprocessor itself
        """
        self.compounds_df.dropna(inplace=True)
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
        X = self.compounds_df[self.chemical_columns].to_numpy()
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

    def append_ecbd_links(
        self,
        ecbd_links: pd.DataFrame,
    ) -> MergedAssaysPreprocessor:
        """
        Append ecbd links to the dataframe.

        :param ecbd_links: dataframe of ecbd links to corresponding compounds
        :return: preprocessor itself
        """
        self.compounds_df = self.compounds_df.join(ecbd_links, how="left")
        return self

    def annotate_by_index(
        self, annotator: Callable[[Any], str]
    ) -> MergedAssaysPreprocessor:
        """
        Annotates the dataframe by a given annotator function

        :param annotator: function to annotate the dataframe
        :return: preprocessor itself
        """
        self.compounds_df["annotation"] = self.compounds_df.index.map(annotator)
        return self

    def get_processed_df(self) -> pd.DataFrame:
        """
        Get the processed dataframe

        :return: processed dataframe
        """
        return self.compounds_df
