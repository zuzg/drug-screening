from __future__ import annotations

import pandas as pd
import numpy as np

from typing import Protocol, Callable, Any

from sklearn.preprocessing import StandardScaler


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
        self.chemical_columns = chemical_columns
        self.compounds_df = raw_compounds_df.set_index(key_column)

    def restrict_to_chemicals(self) -> MergedAssaysPreprocessor:
        self.compounds_df = self.compounds_df[self.chemical_columns]
        return self

    def drop_na(self) -> MergedAssaysPreprocessor:
        self.compounds_df.dropna(inplace=True)
        return self

    def rename_chemical_columns(
        self, rename_func: Callable[[str], str]
    ) -> MergedAssaysPreprocessor:
        new_names = {
            old_name: rename_func(old_name) for old_name in self.chemical_columns
        }
        self.compounds_df = self.compounds_df.rename(columns=new_names)
        return self

    def normalize_columns(self, columns: list[str]) -> MergedAssaysPreprocessor:
        self.compounds_df[columns] = StandardScaler().fit_transform(
            self.compounds_df[columns]
        )
        return self

    def apply_projection(
        self,
        projector: Projector,
        projection_name: str,
        just_transform: bool = False,
    ) -> MergedAssaysPreprocessor:
        X = self.compounds_df[self.chemical_columns].to_numpy()
        if just_transform:
            X_projected = projector.transform(X)
        else:
            X_projected = projector.fit_transform(X)
        suffixes = ["X", "Y"]
        if X_projected.shape[1] > 2:
            suffixes = range(X_projected.shape[0])
        for suffix, col in zip(suffixes, X_projected.T):
            self.compounds_df[f"{projection_name}_{suffix}"] = col
        return self

    def append_ecbd_links(
        self,
        ecbd_links: pd.DataFrame,
    ) -> MergedAssaysPreprocessor:
        self.compounds_df = self.compounds_df.join(ecbd_links, how="left")
        return self

    def annotate_by_index(
        self, annotator: Callable[[Any], str]
    ) -> MergedAssaysPreprocessor:
        self.compounds_df["annotation"] = self.compounds_df.index.map(annotator)
        return self

    def get_processed_df(self) -> pd.DataFrame:
        return self.compounds_df
