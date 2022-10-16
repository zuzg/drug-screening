import pytest
import numpy as np

from src.clustering import (
    KMeansSingleDimensionalClustererFinder,
    FisherJenksSingleDimensionalClustererFinder,
)
from src.clustering.single_dimentional_clusterer_finder import ClustererFinderException


@pytest.mark.parametrize(
    "clusterer_finder_class",
    [
        KMeansSingleDimensionalClustererFinder,
        FisherJenksSingleDimensionalClustererFinder,
    ],
)
class TestSingleDimensionalClustererFindersValidation:
    def test_raises_exception_if_provided_k_is_less_than_2(
        self, clusterer_finder_class
    ):
        with pytest.raises(ClustererFinderException):
            clusterer_finder_class(max_k=1, scoring_function=lambda *args: 0)

    def test_raises_exception_if_provided_series_not_1d(self, clusterer_finder_class):
        finder = clusterer_finder_class(max_k=3, scoring_function=lambda *args: 0)
        with pytest.raises(ClustererFinderException):
            finder.cluster_data_series(np.zeros((2, 2)))


class MockScorer:
    def __init__(self):
        self.scores = [1, 2, 3, 4, 5]

    def __call__(self, *args):
        if self.scores:
            return self.scores.pop(0)
        return 0


@pytest.mark.parametrize(
    "clusterer_finder",
    [
        KMeansSingleDimensionalClustererFinder(
            scoring_function=MockScorer(), max_k=6, random_seed=34
        ),
        FisherJenksSingleDimensionalClustererFinder(
            scoring_function=MockScorer(), max_k=6
        ),
    ],
)
class TestSingleDimensionalClustererFindersClustering:
    mock_series = np.array([1, 2, 3, 4, 5, 6])

    def test_sets_best_k_according_to_best_score(self, clusterer_finder):
        clusterer_finder.cluster_data_series(self.mock_series)
        assert clusterer_finder.best_k == 6
        assert clusterer_finder.best_score == 5

    def test_returns_labels_matching_best_k(self, clusterer_finder):
        labels = clusterer_finder.cluster_data_series(self.mock_series)
        assert max(labels) == (len(labels) - 1)

    def test_returns_label_for_each_element_in_the_series(self, clusterer_finder):
        labels = clusterer_finder.cluster_data_series(self.mock_series)
        assert len(labels) == len(self.mock_series)
