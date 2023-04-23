import argparse
import os

import pandas as pd
import numpy as np


def setup_argparser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Generate mock assay data")
    parser.add_argument(
        "--output-base-name",
        type=str,
        default="MockAssay {num}.xlsx",
    )
    parser.add_argument(
        "--num-rows",
        type=int,
        required=True,
    )
    parser.add_argument(
        "--assay-count",
        type=int,
        default=1,
    )
    parser.add_argument(
        "--out-folder",
        type=str,
        default="out",
    )
    return parser


def generate_assay(num_rows: int, suffix: int) -> pd.DataFrame:
    compound_ids = np.arange(num_rows)
    values = np.random.rand(num_rows)
    return pd.DataFrame(
        {
            f"Assay {suffix} - cmpd Id": compound_ids,
            "% ACTIVATION": values,
        }
    )


if __name__ == "__main__":
    parser = setup_argparser()
    args = parser.parse_args()
    if not os.path.exists(args.out_folder):
        os.makedirs(args.out_folder)
    for i in range(args.assay_count):
        assay = generate_assay(args.num_rows, i)
        assay.to_excel(
            f"{args.out_folder}/{args.output_base_name.format(num=i)}", index=False
        )
