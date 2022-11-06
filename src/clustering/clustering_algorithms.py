import sys
if '../' not in sys.path:
    sys.path.append('../')

import seaborn as sns
import pandas as pd
import numpy as np

from sklearn import metrics
from sklearn.model_selection import ParameterGrid
from matplotlib import pyplot as plt
from jenkspy import JenksNaturalBreaks

from src.clustering import SingleDimensionalClustererFinder, SklearnSingleDimensionalClustererFinder, GeneralClustererFinder
from sklearn.cluster import AgglomerativeClustering
from sklearn.cluster import DBSCAN
import scipy.cluster.hierarchy as sch
from sklearn.preprocessing import normalize

def get_metric(name: str):
    if(name == "silhouette"):
        return metrics.silhouette_score
    if(name == "davies_bouldin"):
        return lambda *args, **kwargs: -metrics.davies_bouldin_score(*args, **kwargs)


def AHC_algorithm(data: np.array, metric = "silhouette") -> np.array:
    """
    Function executing AHC algorithm on one and multi dimensional data.

    :param data: np.array values to be clustered

    :param metric: str names of metrics ["silhouette", "davies_bouldin"]

    :return: cluster indices for consecutive points
    """
    m = get_metric(metric)
    AHC_params = ParameterGrid({"n_clusters": range(2, 10), "linkage":['ward', 'average']})

    if(len(data.shape) == 1):
        AHC_clusterer_finder = SklearnSingleDimensionalClustererFinder(
            param_grid = AHC_params, 
            scoring_function = m,
            clusterer = AgglomerativeClustering(n_clusters=2)
        )
    else:
        data = normalize(data, axis=0, norm='max')
        AHC_clusterer_finder = GeneralClustererFinder(
            param_grid = AHC_params, 
            scoring_function = m,
            clusterer = AgglomerativeClustering()
        )

    return AHC_clusterer_finder.cluster_data_series(data)

def DB_scan_algorithm(data: np.array, metric = "silhouette") -> np.array:
    """
    Function executing DB_scan algorithm on one and multi dimensional data.

    :param data: np.array values to be clustered

    :param metric: str names of metrics ["silhouette", "davies_bouldin"]

    :return: cluster indices for consecutive points
    """
    m = get_metric(metric)
    DB_scan_params = ParameterGrid({"eps": [0.1,0.2,0.3], "min_samples":[2,3]})

    if(len(data.shape) == 1):
        DB_scan_clusterer_finder = SklearnSingleDimensionalClustererFinder(
            param_grid = DB_scan_params, 
            scoring_function = m,
            clusterer = DBSCAN()
        )
    else:
        data = normalize(data, axis=0, norm='max')
        DB_scan_clusterer_finder = GeneralClustererFinder(
            param_grid = DB_scan_params, 
            scoring_function = m,
            clusterer = DBSCAN()
        )

    return DB_scan_clusterer_finder.cluster_data_series(data)
