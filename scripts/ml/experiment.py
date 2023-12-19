import neptune
import neptune.integrations.sklearn as npt_utils
import numpy as np
import pandas as pd
from sklearn.base import BaseEstimator
from sklearn.metrics import mean_squared_error
from sklearn.experimental import enable_halving_search_cv  # noqa
from sklearn.model_selection import HalvingGridSearchCV
from sklearn.pipeline import Pipeline
import structlog
from tdc.single_pred import Tox
from tqdm import tqdm
from typing import List

from scripts.ml.config import ComponentConfig, MLTrainingConfig, SingleExperimentConfig
from consts import (
    FEATURE_SELECTORS_DICT,
    HP_DICT,
    MODELS_DICT,
    NEPTUNE_PROJECT,
    SCALERS_DICT,
)
from utils.chem import featurize_datasets
from utils.imbalance import balance_dataset

_logger = structlog.get_logger()


class ToxicityPredictionExperiment:
    """
    Class for toxicity regression
    """

    def __init__(self, cfg: MLTrainingConfig) -> None:
        """
        :param cfg: ml training config
        """
        self.cfg: MLTrainingConfig = cfg
        self.X_train: np.ndarray
        self.y_train: np.ndarray
        self.X_test: np.ndarray
        self.y_test: np.ndarray

    def save_ndarray(self, arr: np.ndarray, filename: str) -> None:
        """
        Save array to csv

        :param arr: array to be saved
        :param filename: filename
        """
        df = pd.DataFrame(arr)
        df.to_csv(self.cfg.data_dir / filename, index=False)

    def save_dataset(self) -> None:
        """
        Save processed dataset
        """
        _logger.info("Saving dataset")
        self.save_ndarray(self.X_train, "x_train.csv")
        self.save_ndarray(self.X_test, "x_test.csv")
        self.save_ndarray(self.y_train, "y_train.csv")
        self.save_ndarray(self.y_test, "y_test.csv")

    def read_dataset(self) -> None:
        """
        Read saved dataset to arrays
        """
        _logger.info("Reading dataset")
        self.X_train = np.genfromtxt(
            self.cfg.data_dir / "x_train.csv", skip_header=1, delimiter=","
        )
        self.X_test = np.genfromtxt(
            self.cfg.data_dir / "x_test.csv", skip_header=1, delimiter=","
        )
        self.y_train = np.genfromtxt(self.cfg.data_dir / "y_train.csv", skip_header=1)
        self.y_test = np.genfromtxt(self.cfg.data_dir / "y_test.csv", skip_header=1)

    def prepare_dataset(self) -> None:
        """
        1. Download data from tdc
        2. Split dataset
        3. Featurize
        4. Balance
        """
        if self.cfg.generate_dataset:
            data = Tox(name=self.cfg.dataset_name, path=self.cfg.data_dir)
            split = data.get_split(method="scaffold")
            train_raw = pd.concat([split["train"], split["valid"]])
            test_raw = split["test"]
            _logger.info(f"train: {len(train_raw)}, test: {len(test_raw)}")
            self.X_train, self.X_test = featurize_datasets([train_raw, test_raw])
            self.y_train, self.y_test = (
                train_raw.Y.to_numpy(),
                test_raw.Y.to_numpy(),
            )
            self.save_dataset()
        else:
            self.read_dataset()

        if self.cfg.balance_dataset:
            _logger.info("Balancing dataset")
            self.X_train, self.y_train = balance_dataset(self.X_train, self.y_train)

    def prepare_pipeline(self, config: SingleExperimentConfig) -> Pipeline:
        """
        Prepare pipeline

        :param config: single experiment config
        :return: prepared pipeline
        """
        components = []
        if config.feature_selection.component:
            components.append(("feature_selection", config.feature_selection.component))
        if config.scaler.component:
            components.append(("scaler", config.scaler.component))

        if self.cfg.hp_tuning and config.model.name in HP_DICT:
            components.append(
                ("model", self.tune_hp(config.model.component, config.model.name))
            )
        else:
            components.append(("model", config.model.component))
        return Pipeline(components)

    def prepare_experiment_configs(self) -> List[SingleExperimentConfig]:
        """
        Create combinations of experiment parameters

        :return: list of single experiment configs
        """
        configs = []
        for fs_name, fs in FEATURE_SELECTORS_DICT.items():
            for scaler_name, scaler in SCALERS_DICT.items():
                for model_name, model in MODELS_DICT.items():
                    fs_cfg = ComponentConfig(fs_name, fs)
                    scaler_cfg = ComponentConfig(scaler_name, scaler)
                    model_cfg = ComponentConfig(model_name, model)
                    single_exp_cfg = SingleExperimentConfig(
                        fs_cfg, scaler_cfg, model_cfg
                    )
                    configs.append(single_exp_cfg)
        return configs

    def get_tags(self, config: SingleExperimentConfig) -> List[str]:
        """
        Prepare tags to log to neptune.ai

        :config: single experiment config
        :return: list with tags
        """
        tags = [config.model.name, config.scaler.name, config.feature_selection.name]
        if self.cfg.balance_dataset:
            tags.append("balanced")
        if self.cfg.hp_tuning:
            tags.append("hp_tuning")
        return tags

    def tune_hp(self, model: BaseEstimator, model_name: str) -> BaseEstimator:
        """
        Create grid search for hp tuning

        :param model: model to tune
        :param model_name: model name
        :return: grid search object
        """
        _logger.info("Preparing hyperparameter search")
        params = HP_DICT[model_name]
        gs = HalvingGridSearchCV(
            estimator=model,
            param_grid=params,
            scoring="neg_mean_absolute_error",
            refit="neg_mean_absolute_error",
            return_train_score=True,
        )
        return gs

    def run_experiment(self, config: SingleExperimentConfig) -> None:
        """
        Run single experiment and log it to neptune

        :param config: single experiment config
        """
        run = neptune.init_run(project=NEPTUNE_PROJECT, tags=self.get_tags(config))
        pipeline = self.prepare_pipeline(config)

        _logger.info("Fitting")
        pipeline.fit(
            self.X_train,
            self.y_train,
        )
        _logger.info("Logging to neptune")
        run["summary"] = npt_utils.create_regressor_summary(
            pipeline,
            self.X_train,
            self.X_test,
            self.y_train,
            self.y_test,
            nrows=10,
            log_charts=False,
        )
        preds = pipeline.predict(X=self.X_test)
        run["test/scores/rmse"] = mean_squared_error(self.y_test, preds, squared=False)
        run.stop()

    def run_trainings(self):
        """
        Run all prepared experiments
        """
        experiment_configs = self.prepare_experiment_configs()
        for config in tqdm(experiment_configs, desc="Executing individual experiments"):
            self.run_experiment(config=config)

        _logger.info("Successfully finished running all experiments.")
