import numpy as np

from .single_dimensional_clusterer_finder import (
    SingleDimensionalClustererFinder,
)


class SklearnSingleDimensionalClustererFinder(SingleDimensionalClustererFinder):
    """
    Clusterer Finder compatible with sklearn api (sklearn clusterers require series to be 2D)
    """

    def _prepare_series_for_prediction(self, series: np.array) -> np.array:
        return super()._prepare_series_for_prediction(series).reshape(-1, 1)
