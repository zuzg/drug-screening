import numpy as np

from typing import Iterable, Protocol, Callable
from copy import deepcopy


class Clusterer(Protocol):
    """
    Clusterer structure required by the GeneralCLustererFinder.
    """

    def fit(self, data: np.ndarray) -> None:
        ...

    def predict(self, data: np.ndarray) -> np.ndarray:
        ...

    def fit_predict(self, data: np.ndarray) -> np.ndarray:
        ...

    def set_params(self, **params: dict) -> None:
        ...


class GeneralClustererFinder:
    """
    General Clusterer Finder for Grid Searching through parameters in order to find the best set.
    (It is different from sklearn.model_selection.GridSearchCV in that it is not forced to use cross validation,
    which we do not want to use in clustering and stores scores for each combination of parameters)
    """

    def __init__(
        self,
        param_grid: Iterable[dict],
        clusterer: Clusterer,
        scoring_function: Callable[[np.array, np.array], float],
    ) -> None:
        """
        :param param_grid: Iterable of dictionaries with parameters for the clusterer

        :param clusterer: Clustering Algorithm (Clusterer) to be used, has to have
        fit, predict and set_params methods

        :param scoring_function: Scoring function to determine best parameters (higher is better),
        takes series (2D) and labels (1D) as arguments, returns numeric score
        """
        self.param_grid = param_grid
        self.clusterer = clusterer
        self.scoring_function = scoring_function
        self.scores = []
        self.best_score = -np.inf
        self.best_params = {}
        self.best_clusterer = None
        self.cached_best_prediction = None

    def _prepare_series_for_prediction(self, series: np.array) -> np.array:
        return series

    def _prepare_series_for_scoring(self, series: np.array) -> np.array:
        return series

    def _check_update_best(
        self, score: float, params: dict, prediction: np.array
    ) -> None:
        if score > self.best_score:
            self.best_score = score
            self.best_clusterer = deepcopy(
                self.clusterer
            )  # Deepcopy clusterer since he may be mutated in clustering process
            self.best_params = params
            self.cached_best_prediction = prediction

    def cluster_data_series(self, series: np.array, verbose: bool = False, joint_fit_predict = False) -> np.array:
        """
        Performs Grid Search with passed Parameter Grid and Clustering Algorithm (Clusterer)
        on the given data series.
        Updates the best found parameters and results, as well as the best clusterer.
        Returns the best prediction.

        :param series: series of numeric data which should be clustered

        :param verbose: if True, prints additional information

        :return: list of labels denoting the cluster of each data point
        """
        series_for_clusterer = self._prepare_series_for_prediction(series)
        series_for_scoring = self._prepare_series_for_scoring(series)
        for params in self.param_grid:
            self.clusterer.set_params(**params)
            if joint_fit_predict:
                labels = self.clusterer.fit_predict(series_for_clusterer)
            else:
                self.clusterer.fit(series_for_clusterer)
                labels = self.clusterer.predict(series_for_clusterer)
            score = self.scoring_function(series_for_scoring, labels)
            if verbose:
                print(f"Params: {params} | Score: {score}")
            self._check_update_best(score, params, labels)
            self.scores.append({"score": score, **params})
        if verbose:
            print("\nDONE\n")
            print(f"Best Score: {self.best_score}")
            print(f"Best Params: {self.best_params}")
        return self.cached_best_prediction
