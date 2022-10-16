import numpy as np

from typing import Protocol, Callable
from abc import ABC, abstractmethod


class Clusterer(Protocol):
    def fit(self, data: np.ndarray) -> None:
        ...

    def predict(self, data: np.ndarray) -> np.ndarray:
        ...


class SingleDimensionalClustererFinder(ABC):
    """
    Base class for finding best clusterer paremeters for single dimensional data series
    """

    def __init__(
        self, scoring_function: Callable[[np.array, np.array], float], max_k: int = 50
    ) -> None:
        self.scoring_function = scoring_function
        self.max_k = max_k
        self.best_score = -np.inf
        self.best_k = None
        self.best_clusterer = None
        self.cached_best_prediction = None

    @abstractmethod
    def _initialize_clusterer(self, k: int) -> Clusterer:
        ...

    def _prepare_series_for_prediction(self, series: np.array) -> np.array:
        return np.sort(series)

    def _prepare_series_for_scoring(self, series: np.array) -> np.array:
        return np.sort(series).reshape(-1, 1)

    def _check_update_best(
        self, clusterer: Clusterer, score: float, k: int, prediction: np.array
    ) -> None:
        if score > self.best_score:
            self.best_score = score
            self.best_clusterer = clusterer
            self.best_k = k
            self.cached_best_prediction = prediction

    def cluster_data_series(
        self, series: np.array, verbose: bool = False
    ) -> list[np.array]:
        """
        Searches for best number of classes (clusterer parameter) for given data series,
        updates the best found parameters and results, as well as the best clusterer.
        Returns the best prediction.

        :param series: series of numeric data which should be clustered
        :param verbose: if True, prints additional information
        :return: list of arrays that represent clusters
        """
        series_for_clusterer = self._prepare_series_for_prediction(series)
        series_for_scoring = self._prepare_series_for_scoring(series)
        for k in range(2, self.max_k + 1):
            clusterer = self._initialize_clusterer(k)
            clusterer.fit(series_for_clusterer)
            labels = clusterer.predict(series_for_clusterer)
            score = self.scoring_function(series_for_scoring, labels)
            if verbose:
                print(f"K: {k:<3} Score: {score}")
            self._check_update_best(clusterer, score, k, labels)
        if verbose:
            print(f"Best K: {self.best_k}")
            print(f"Best score: {self.best_score}")
        return self.cached_best_prediction
