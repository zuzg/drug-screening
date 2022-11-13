import sys
if '../' not in sys.path:
    sys.path.append('../')

import pandas as pd
import numpy as np

from typing import Callable
from sklearn.model_selection import ParameterGrid


from src.clustering import GeneralClustererFinder
from sklearn.cluster import AgglomerativeClustering, DBSCAN, KMeans
from sklearn.mixture import GaussianMixture
from sklearn.preprocessing import normalize

RANDOM_STATE = 31
CLUSTERING_CONFIG = {
    "KMeans":{
        "clusterer": KMeans(),
        "param_grid": ParameterGrid({
            "n_clusters": range(2, 16),
            "random_state": [RANDOM_STATE]
        }),
    },

    "GaussianMixture": {
        "clusterer": GaussianMixture(),
        "param_grid": ParameterGrid({
            "n_components": range(2, 16),
            "random_state": [RANDOM_STATE]
        }),
    },

    "AgglomerativeClustering":{
        "clusterer": AgglomerativeClustering(),
        "param_grid": ParameterGrid({
            "n_components": range(2, 10),
            "linkage": ['ward', 'average'],
            "random_state": [RANDOM_STATE]
        }),
    },

    "DBSCAN": {
        "clusterer": DBSCAN(),
        "param_grid": ParameterGrid({
            "eps": [0.1,0.2,0.3], 
            "min_samples":[2,3],
            "random_state": [RANDOM_STATE]
        }),
    }
}

def perform_clustering(data_series: np.ndarray, metric: Callable[[np.ndarray, np.ndarray], float], index: pd.Series, algorithms=None) -> pd.DataFrame:
    """
    Perform clustering with pre-specified clustering methods if no algorithm is specified, 
    then all clustering algorithms from CLUSTERING_CONFIG will be executed

    :param data_series: np.ndarray vith values to be clustered

    :param metric: metric according to which the algorithms will be evaluated
    
    :param index: pd.Series of indices of elements to be clustered

    :return: pd.DataFrame containing elements indices along with their clusteringusing different algorithms
    """
    df = pd.DataFrame(index=index)
    
    if algorithms is None:
        for algorithm in CLUSTERING_CONFIG:
            
            clusterer_finder = GeneralClustererFinder(
                param_grid=CLUSTERING_CONFIG[algorithm]["param_grid"],
                clusterer=CLUSTERING_CONFIG[algorithm]["clusterer"],
                scoring_function=metric
            )
            print(f"==== CLUSTERING WITH {algorithm} ====")
            clusterer_finder.cluster_data_series(data_series, verbose=True)
            df[f"labels_{algorithm}"] = clusterer_finder.cached_best_prediction
    
    else:
        for algorithm in algorithms:
            try:
                clusterer_finder = GeneralClustererFinder(
                    param_grid=CLUSTERING_CONFIG[algorithm]["param_grid"],
                    clusterer=CLUSTERING_CONFIG[algorithm]["clusterer"],
                    scoring_function=metric
                )
                print(f"==== CLUSTERING WITH {algorithm} ====")
                clusterer_finder.cluster_data_series(data_series, verbose=True)
                df[f"labels_{algorithm}"] = clusterer_finder.cached_best_prediction
            except:
                print(f'Clustering algorithm {algorithm} not found!')
                continue
    return df
