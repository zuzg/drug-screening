import numpy as np

from .general_clusterer_finder import GeneralClustererFinder


class SingleDimensionalClustererFinder(GeneralClustererFinder):
    """
    Clusterer specialized for 1D clustering where it is always beneficial to sort the series
    before clustering.

    Ensures the passed series is 1D.
    """

    def _prepare_series_for_prediction(self, series: np.array) -> np.array:
        if len(series.shape) > 1:
            raise ValueError(
                f"Series must be one dimensional! (current series shape: {series.shape})"
            )
        return np.sort(series)

    def _prepare_series_for_scoring(self, series: np.array) -> np.array:
        return np.sort(series).reshape(-1, 1)
