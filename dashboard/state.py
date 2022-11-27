import pandas as pd

from dataclasses import dataclass, field


@dataclass
class GlobalState:
    """
    Global state of the application, keeps the global dataframe in memory.
    """

    crucial_columns: list[str] = field(default_factory=list)
    df: pd.DataFrame = pd.DataFrame()

    def set_dataframe(self, df: pd.DataFrame) -> None:
        """
        Sets the global dataframe.
        Extracts crucial columns for vizualization from the dataframe.

        :param df: dataframe
        """

        self.df = df
        self.crucial_columns = [
            column
            for column in df.columns
            if ("% ACTIVATION" in column or "% INHIBITION" in column)
            and "(" not in column  # filters out stuff like std(% ACTIVATION) etc
        ]

    @property
    def strict_df(self) -> pd.DataFrame:
        """
        Returns the global dataframe with only the crucial columns.

        :return: dataframe with only the crucial columns
        """

        return self.df[self.crucial_columns]
