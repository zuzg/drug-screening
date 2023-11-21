from typing import Tuple

import numpy as np
import resreg


def balance_dataset(X: np.ndarray, y: np.ndarray) -> Tuple[np.ndarray, np.ndarray]:
    relevance = resreg.sigmoid_relevance(y, cl=1.25, ch=3.5)
    X_balanced, y_balanced = resreg.smoter(X, y, relevance=relevance)
    return X_balanced, y_balanced
