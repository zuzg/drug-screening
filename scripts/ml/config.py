from dataclasses import dataclass
import structlog
from pathlib import Path
from typing import Optional

from sklearn.base import BaseEstimator

logger = structlog.get_logger()


@dataclass
class MLTrainingConfig:
    dataset_name: str
    data_dir: Path
    output_dir: Path
    balance_dataset: bool

    def log_self(self) -> None:
        logger.info(f"Running with following config: {self}")


@dataclass
class ComponentConfig:
    name: str
    component: Optional[BaseEstimator] = None
    params_str: Optional[str] = None


@dataclass
class SingleExperimentConfig:
    # dim_red: ComponentConfig
    scaler: ComponentConfig
    model: ComponentConfig
