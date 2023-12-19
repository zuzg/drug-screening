import argparse

from config import MLTrainingConfig
from consts import DATA_FOLDER_NAME


def parse_args() -> MLTrainingConfig:
    parser = argparse.ArgumentParser()

    parser.add_argument("--dataset_name", type=str, default="LD50_Zhu")
    parser.add_argument("--generate_dataset", type=bool, default=False)
    parser.add_argument("--balance_dataset", type=bool, default=True)
    parser.add_argument("--hp_tuning", type=bool, default=True)
    parser.add_argument(
        "--data_dir",
        type=str,
        default=DATA_FOLDER_NAME,
    )

    args = parser.parse_args()
    cfg = MLTrainingConfig(**vars(args))
    cfg.log_self()
    return cfg
