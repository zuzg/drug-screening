import pandas as pd

from dataclasses import dataclass


@dataclass
class GlobalState:
    df: pd.DataFrame = pd.DataFrame()
