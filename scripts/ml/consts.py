from pathlib import Path
from typing import Dict, Optional

import xgboost as xgb
from sklearn.base import BaseEstimator
from sklearn.ensemble import (
    AdaBoostRegressor,
    BaggingRegressor,
    RandomForestRegressor,
)
from sklearn.linear_model import (
    PassiveAggressiveRegressor,
    Perceptron,
)
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

NEPTUNE_PROJECT = "drug-screening/toxicity-prediction"

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

HP_DICT = {
    "RandomForestRegressor": {
        "n_estimators": [10, 20, 50, 100],
        "n_estimators": [10, 20, 50, 70, 100],
        "max_depth": [None, 5, 7, 10, 15],
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
    "none": None,
    "standardscaler": StandardScaler(),
    "minmaxscaler": MinMaxScaler(),
    "robustscaler": RobustScaler(),
}
