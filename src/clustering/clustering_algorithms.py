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
import scipy.cluster.hierarchy as sch
from sklearn.preprocessing import normalize

def get_metric(name: str):
    if(name == "silhouette"):
        return metrics.silhouette_score
    if(name == "davies_bouldin"):
        return lambda *args, **kwargs: -metrics.davies_bouldin_score(*args, **kwargs)


def AHC_algorithm(data: np.array, metric = "silhouette", norm = True) -> np.array:
    """
    Function executing AHC algorithm on one and multi dimensional data.

    :param data: np.array values to be clustered

    :return: cluster indices for consecutive points
    """
    print(data)
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
            clusterer = AgglomerativeClustering(n_clusters=2)
        )

    return AHC_clusterer_finder.cluster_data_series(data)


