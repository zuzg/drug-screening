from pathlib import Path
from typing import Any, Dict, List, Optional

import xgboost as xgb
from sklearn.base import BaseEstimator
from sklearn.ensemble import (
    AdaBoostRegressor,
    BaggingRegressor,
    RandomForestRegressor,
)
from sklearn.feature_selection import r_regression, SelectKBest, VarianceThreshold
from sklearn.linear_model import PassiveAggressiveRegressor
from sklearn.neighbors import KNeighborsRegressor
from sklearn.neural_network import MLPRegressor
from sklearn.preprocessing import (
    MinMaxScaler,
    RobustScaler,
    StandardScaler,
)
from sklearn.svm import SVR
from sklearn.tree import DecisionTreeRegressor


ROOT_DIR: Path = Path(__file__).resolve().parents[2]
DATA_FOLDER_NAME: Path = ROOT_DIR / "data"
OUTPUT_FOLDER_NAME: Path = ROOT_DIR / "output"

NEPTUNE_PROJECT: str = "drug-screening/toxicity-prediction"

MODELS_DICT: Dict[str, BaseEstimator] = {
    "RandomForestRegressor": RandomForestRegressor(),
    "KNeighborsRegressor": KNeighborsRegressor(),
    "SVR": SVR(),
    "AdaBoostRegressor": AdaBoostRegressor(),
    "DecisionTreeRegressor": DecisionTreeRegressor(),
    "BaggingRegressor": BaggingRegressor(),
    "PassiveAggressiveRegressor": PassiveAggressiveRegressor(),
    "MLPRegressor": MLPRegressor(),
    "XGBRegressor": xgb.XGBRegressor(),
}

HP_DICT: Dict[str, Dict[str, List[Any]]] = {
    "RandomForestRegressor": {
        "n_estimators": [50, 100, 150],
        "max_depth": [None, 5, 10, 15],
    },
    "PassiveAggressiveRegressor": {"C": [0.5, 1, 5]},
    "XGBRegressor": {
        "n_estimators": [20, 50, 70, 100],
        "max_depth": [None, 5, 10, 15],
        "learning_rate": [10e-1, 10e-2, 10e-3],
    },
    "MLPRegressor": {
        "hidden_layer_sizes": [(50, 50, 50), (50, 100, 50), (100,)],
        "activation": ["logistic", "tanh", "relu"],
        "solver": ["sgd", "adam"],
        "alpha": [0.0001, 0.001],
        "learning_rate": ["constant", "invscaling", "adaptive"],
    },
}

SCALERS_DICT: Dict[str, Optional[BaseEstimator]] = {
    "NoScaler": None,
    "StandardScaler": StandardScaler(),
    "MinMaxScaler": MinMaxScaler(),
    "RobustScaler": RobustScaler(),
}

FEATURE_SELECTORS_DICT: Dict[str, Optional[BaseEstimator]] = {
    "NoFeatureSelector": None,
    "VarianceThreshold": VarianceThreshold(),
    "SelectKBest": SelectKBest(r_regression, k=20),
}
