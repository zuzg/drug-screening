from typing import List

import numpy as np
import pandas as pd
from deepchem import deepchem


def featurize_datasets(datasets: List[pd.DataFrame]) -> List[np.ndarray]:
    """
    Calculate rdkit descriptors for datasets

    :param datasets: list of datasets to featurize
    :return: list with featurized datasets
    """
    rdkit = deepchem.feat.RDKitDescriptors()
    featurized = []
    for dataset in datasets:
        featurized.append(rdkit.featurize(dataset.Drug.to_list()))
    return featurized
