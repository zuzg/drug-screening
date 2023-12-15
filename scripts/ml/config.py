from dataclasses import dataclass
import structlog
from pathlib import Path
from typing import Optional

from sklearn.base import BaseEstimator

logger = structlog.get_logger()


@dataclass
class MLTrainingConfig:
    """
    Class with ml training parameters
    """

    dataset_name: str
    data_dir: Path
    generate_dataset: bool
    balance_dataset: bool
    hp_tuning: bool

    def log_self(self) -> None:
        """
        Log current config
        """
        logger.info(f"Running with following config: {self}")


@dataclass
class ComponentConfig:
    """
    Class with config for component
    """

    name: str
    component: Optional[BaseEstimator] = None
    params_str: Optional[str] = None


@dataclass
class SingleExperimentConfig:
    """
    Class with config for single experiment
    """

    feature_selection: ComponentConfig
    scaler: ComponentConfig
    model: ComponentConfig
