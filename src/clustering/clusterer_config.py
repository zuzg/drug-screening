import pandas as pd
import numpy as np

from typing import Callable, Iterable
from dataclasses import dataclass

from src.clustering import GeneralClustererFinder
from .general_clusterer_finder import Clusterer

RANDOM_STATE = 31


@dataclass
class ClustererConfig:
    """
    Class parameters and clustering algorithm
    """

    clusterer: Clusterer
    param_grid: Iterable[Iterable]


def perform_clusterer_search_from_config(
    data_series: np.ndarray,
    metric: Callable[[np.ndarray, np.ndarray], float],
    index: pd.Series,
    clustering_config: dict[str, ClustererConfig],
) -> pd.DataFrame:
    """
    Perform clustering with pre-specified clustering configurations.

    :param data_series: np.ndarray vith values to be clustered

    :param metric: metric according to which the algorithms will be evaluated

    :param index: pd.Series of indices of elements to be clustered

    :param clustering_config: dictionary of clustering configuration with names as keys

    :return: pd.DataFrame containing elements indices along with their clusteringusing different algorithms
    """
    df = pd.DataFrame(index=index)
    for name, config in clustering_config.items():
        clusterer_finder = GeneralClustererFinder(
            param_grid=config.param_grid,
            clusterer=config.clusterer,
            scoring_function=metric,
        )
        print(f"==== CLUSTERING WITH {name} ====")
        clusterer_finder.cluster_data_series(data_series, verbose=True)
        df[f"labels_{name}"] = clusterer_finder.cached_best_prediction
    return df
