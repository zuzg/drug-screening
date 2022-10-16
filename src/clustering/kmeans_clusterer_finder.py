import numpy as np

from typing import Callable

from sklearn.cluster import KMeans

from .single_dimentional_clusterer_finder import (
    SingleDimensionalClustererFinder,
    Clusterer,
)


class KMeansSingleDimensionalClustererFinder(SingleDimensionalClustererFinder):
    """
    Utilizes KMeans clustering algorithm to find best KMeans clusterer parameters
    """

    def __init__(
        self,
        scoring_function: Callable[[np.array, np.array], float],
        random_seed: int | None = None,
        max_k: int = 50,
    ) -> None:
        super().__init__(scoring_function, max_k)
        self.random_seed = random_seed

    def _initialize_clusterer(self, k: int) -> Clusterer:
        return KMeans(n_clusters=k, random_state=self.random_seed)

    def _prepare_series_for_prediction(self, series: np.array) -> np.array:
        return super()._prepare_series_for_prediction(series).reshape(-1, 1)
