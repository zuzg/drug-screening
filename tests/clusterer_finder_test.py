import pytest
import numpy as np

from unittest.mock import Mock
from src.clustering import (
    GeneralClustererFinder,
    SingleDimensionalClustererFinder,
    SklearnSingleDimensionalClustererFinder,
)


class MockScorer:
    def __init__(self):
        self.scores = [1, 2, 3, 4, 5]

    def __call__(self, *args):
        if self.scores:
            return self.scores.pop(0)
        return 0


def test_single_dimensional_finder_raises_exception_if_provided_series_not_1d():
    finder = SingleDimensionalClustererFinder([{"test_param": 1}], Mock(), Mock())
    with pytest.raises(ValueError):
        finder.cluster_data_series(np.zeros((2, 2)))


def test_sklearn_single_dimensional_finder_passes_reshaped_series_to_clusterer():
    mock_clusterer = Mock()
    finder = SklearnSingleDimensionalClustererFinder(
        [{"test_param": 1}], mock_clusterer, MockScorer()
    )
    finder.cluster_data_series(np.array([1, 2, 3]))
    assert np.array_equal(mock_clusterer.fit.call_args[0][0], np.array([[1], [2], [3]]))


class TestGeneralClustererFinder:
    mock_series = np.array([1, 2, 3, 4, 5, 6])

    def test_sets_best_params_according_to_best_score(self):
        clusterer_finder = GeneralClustererFinder(
            param_grid=[{"a": 1}, {"a": 2}, {"a": 3}, {"a": 4}, {"a": 5}],
            clusterer=Mock(),
            scoring_function=MockScorer(),
        )
        clusterer_finder.cluster_data_series(self.mock_series)
        assert clusterer_finder.best_params == {"a": 5}
        assert clusterer_finder.best_score == 5

    def test_copies_best_clusterer_instead_of_referencing_it(self):
        mock_clusterer = Mock()
        clusterer_finder = GeneralClustererFinder(
            param_grid=[{"a": 1}, {"a": 2}, {"a": 3}, {"a": 4}, {"a": 5}],
            clusterer=mock_clusterer,
            scoring_function=MockScorer(),
        )
        clusterer_finder.cluster_data_series(self.mock_series)
        assert clusterer_finder.best_clusterer is not mock_clusterer
