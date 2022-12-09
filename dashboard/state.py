import pandas as pd

from dataclasses import dataclass, field

from src.data.parse_data import get_projections


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
        self.projections_df = get_projections(self.strict_df, get_3d=False)

    @property
    def strict_df(self) -> pd.DataFrame:
        """
        Returns the global dataframe with only the crucial columns.

        :return: dataframe with only the crucial columns
        """

        return self.df[["CMPD ID"] + self.crucial_columns]

    @property
    def strict_summary_df(self) -> pd.DataFrame:
        """
        Returns the formatted statistical summary dataframe of value columns.

        :return: summary dataframe
        """

        return self.strict_df.describe().round(3).T.reset_index(level=0)
