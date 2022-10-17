import jenkspy

from .single_dimensional_clusterer_finder import (
    SingleDimensionalClustererFinder,
    Clusterer,
)


class FisherJenksSingleDimensionalClustererFinder(SingleDimensionalClustererFinder):
    """
    Utilizes Fisher-Jenks Natural Breaks algorithm to find best clusterer parameters
    """

    def _initialize_clusterer(self, k: int) -> Clusterer:
        return jenkspy.JenksNaturalBreaks(k)
