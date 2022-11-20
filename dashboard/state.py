import pandas as pd

from dataclasses import dataclass


@dataclass
class GlobalState:
    """
    Global state of the application, keeps the global dataframe in memory.
    """

    df: pd.DataFrame = pd.DataFrame()
