import argparse

from config import MLTrainingConfig
from consts import DATA_FOLDER_NAME, OUTPUT_FOLDER_NAME, ROOT_DIR


def parse_args() -> MLTrainingConfig:
    parser = argparse.ArgumentParser()

    parser.add_argument("--dataset_name", type=str, default="LD50_Zhu")
    parser.add_argument("--balance_dataset", type=bool, default=True)
    parser.add_argument(
        "--data_dir",
        type=str,
        default=DATA_FOLDER_NAME,
    )
    parser.add_argument(
        "--output_dir",
        type=str,
        default=OUTPUT_FOLDER_NAME,
    )

    args = parser.parse_args()
    cfg = MLTrainingConfig(**vars(args))
    cfg.log_self()
    return cfg
