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
from sklearn.cluster import AgglomerativeClustering, DBSCAN, KMeans
from sklearn.mixture import GaussianMixture
import scipy.cluster.hierarchy as sch
from sklearn.preprocessing import normalize

RANDOM_STATE = 31
CLUSTERING_CONFIG = [
    {
        "name": "KMeans",
        "clusterer": KMeans(),
        "param_grid": ParameterGrid({
            "n_clusters": range(2, 16),
            "random_state": [RANDOM_STATE]
        }),
    },
    {
        "name": "GaussianMixture",
        "clusterer": GaussianMixture(),
        "param_grid": ParameterGrid({
            "n_components": range(2, 16),
            "random_state": [RANDOM_STATE]
        }),
    },
    {
        "name": "AHC",
        "clusterer": AgglomerativeClustering(),
        "param_grid": ParameterGrid({
            "n_components": range(2, 10),
            "linkage": ['ward', 'average'],
            "random_state": [RANDOM_STATE]
        }),
    },
    {
        "name": "DBScan",
        "clusterer": DBSCAN(),
        "param_grid": ParameterGrid({
            "eps": [0.1,0.2,0.3], 
            "min_samples":[2,3],
            "random_state": [RANDOM_STATE]
        }),
    }
]

def evaluate_with_metric(data_series: np.ndarray, metric: Callable[[np.ndarray, np.ndarray], float], index: pd.Series) -> pd.DataFrame:
    df = pd.DataFrame(index=index)
    for config in CLUSTERING_CONFIG:
        print(f"==== CLUSTERING WITH {config['name']} ====")
        clusterer_finder = GeneralClustererFinder(
            param_grid=config["param_grid"],
            clusterer=config["clusterer"],
            scoring_function=metric
        )
        clusterer_finder.cluster_data_series(data_series, verbose=True)
        df[f"labels_{config['name']}"] = clusterer_finder.cached_best_prediction
    return df

def summarize_clustering(values: np.ndarray, labels: np.ndarray) -> None:
    all_labels = np.unique(labels).flatten()
    for label in all_labels:
        label_values = values[labels.flatten() == label]
        print(f"Cluster {label}: {len(label_values)} values")
        print(f"\tMean: {np.mean(label_values, axis=0)}")
        print(f"\tStd: {np.std(label_values, axis=0)}")
        print(f"\tMin: {np.min(label_values, axis=0)}")
        print(f"\tMax: {np.max(label_values, axis=0)}")
        print()
