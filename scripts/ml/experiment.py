import neptune
import neptune.integrations.sklearn as npt_utils
import numpy as np
import pandas as pd
from sklearn.metrics import mean_squared_error
from sklearn.pipeline import Pipeline
import structlog
from tdc.single_pred import Tox
from tqdm import tqdm
from typing import List

from scripts.ml.config import ComponentConfig, MLTrainingConfig, SingleExperimentConfig
from consts import MODELS_DICT, NEPTUNE_PROJECT, SCALERS_DICT
from utils.chem import featurize_datasets
from utils.imbalance import balance_dataset

_logger = structlog.get_logger()


class ToxicityPredictionExperiment:
    def __init__(self, cfg: MLTrainingConfig) -> None:
        self.cfg: MLTrainingConfig = cfg
        self.X_train: np.ndarray
        self.y_train: np.ndarray
        self.X_test: np.ndarray
        self.y_test: np.ndarray

    def prepare_dataset(self) -> None:
        data = Tox(name=self.cfg.dataset_name, path=self.cfg.data_dir)
        split = data.get_split()
        train_raw = pd.concat([split["train"], split["valid"]])
        test_raw = split["test"]
        _logger.info(f"train: {len(train_raw)}, test: {len(test_raw)}")
        self.X_train, self.X_test = featurize_datasets([train_raw, test_raw])
        self.y_train, self.y_test = (
            train_raw.Y.to_numpy(),
            test_raw.Y.to_numpy(),
        )
        if self.cfg.balance_dataset:
            _logger.info("Balancing dataset")
            self.X_train, self.y_train = balance_dataset(self.X_train, self.y_train)

    def prepare_pipeline(self, config: SingleExperimentConfig) -> Pipeline:
        components = []
        # if config.dim_reduction:
        #     components.append(("dim_reduction", config.dim_reduction))
        if config.scaler.component:
            components.append(("scaler", config.scaler.component))
        components.append(("model", config.model.component))
        return Pipeline(components)

    def prepare_experiment_configs(self) -> List[SingleExperimentConfig]:
        configs = []
        for scaler_name, scaler in SCALERS_DICT.items():
            for model_name, model in MODELS_DICT.items():
                scaler_cfg = ComponentConfig(scaler_name, scaler)
                model_cfg = ComponentConfig(model_name, model)
                single_exp_cfg = SingleExperimentConfig(scaler_cfg, model_cfg)
                configs.append(single_exp_cfg)
        return configs

    def run_experiment(self, config: SingleExperimentConfig) -> None:
        tags = [config.model.name, config.scaler.name]
        if self.cfg.balance_dataset:
            tags.append("balanced")
        run = neptune.init_run(project=NEPTUNE_PROJECT, tags=tags)
        pipeline = self.prepare_pipeline(config)
        _logger.info("Fitting")
        pipeline.fit(
            self.X_train,
            self.y_train,
        )
        _logger.info("Logging to neptune")
        run["summary"] = npt_utils.create_regressor_summary(
            pipeline["model"],
            self.X_train,
            self.X_test,
            self.y_train,
            self.y_test,
            nrows=100,
            log_charts=False,
        )
        preds = pipeline.predict(X=self.X_test)
        run["test/scores/mse"] = mean_squared_error(self.y_test, preds)
        run.stop()

    def run_trainings(self):
        experiment_configs = self.prepare_experiment_configs()
        for config in tqdm(experiment_configs, desc="Executing individual experiments"):
            self.run_experiment(config=config)

        _logger.info("Successfully finished running all experiments.")
