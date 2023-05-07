from __future__ import annotations
import pandas as pd


class EchoFilesParser:
    def __init__(
        self,
        echo_files: list[str],
    ):
        """
        :param echo_files: list of echo file names
        """
        self.echo_files = echo_files

    def find_marker_rows(self, file: str, markers: tuple[str]) -> list[int]:
        """
        Finds the row numbers of marker lines in a file.

        :param file: file to search
        :param markers: markers to search for
        """
        with open(file) as f:
            markers_rows = list()
            for i, line in enumerate(f):
                if line.strip() in markers:
                    markers_rows.append(i)
                if len(markers_rows) == len(markers):
                    return markers_rows
        return markers_rows

    def parse_files(self) -> EchoFilesParser:
        """
        Preprocesses csv echo files, splits regular records from exceptions.
        """
        if not (all(file.endswith(".csv") for file in self.echo_files)):
            raise ValueError(
                f"Expected files to be of '*.csv' type, provided: {self.echo_files}"
            )

        exception_dfs, echo_dfs = [], []
        for filename in self.echo_files:
            markers = self.find_marker_rows(filename, ("[EXCEPTIONS]", "[DETAILS]"))

            if len(markers) == 2:
                exceptions_line, details_line = markers
                exceptions_df = pd.read_csv(
                    filename,
                    skiprows=exceptions_line + 1,
                    nrows=(details_line - 1) - exceptions_line - 2,
                )
                echo_df = pd.read_csv(filename, skiprows=details_line + 1)
            elif len(markers) == 1:
                exceptions_df = pd.DataFrame()
                echo_df = pd.read_csv(filename, skiprows=markers[0] + 1)
            else:
                echo_df = pd.read_csv(filename)

            echo_df = echo_df[
                ~echo_df[echo_df.columns[0]].str.lower().str.startswith("instrument")
            ]
            exception_dfs.append(exceptions_df)
            echo_dfs.append(echo_df)

        self.exceptions_df = pd.concat(exception_dfs, ignore_index=True)
        self.echo_df = pd.concat(echo_dfs, ignore_index=True)

        return self

    def retain_key_columns(self, columns: list[str] = None) -> EchoFilesParser:
        """
        Retains only the specified columns.

        :param columns: list of columns to retain
        """
        # TODO : include CMPD -> we need to get these column from HTS center
        if columns is None:
            columns = [
                "CMPD ID",
                "Source Plate Barcode",
                "Source Well",
                "Destination Plate Barcode",
                "Destination Well",
                "Actual Volume",
            ]

        retain_echo = list(set(columns).intersection(self.echo_df.columns))
        self.echo_df = self.echo_df[retain_echo]

        retain_exceptions = list(
            set(columns + ["Transfer Status"]).intersection(self.exceptions_df.columns)
        )
        self.exceptions_df = self.exceptions_df[retain_exceptions].sort_index(axis=1)
        return self

    def get_processed_echo_df(self) -> pd.DataFrame:
        """
        Get the processed echo dataframe

        :return: processed dataframe
        """
        return self.echo_df

    def get_processed_exception_df(self) -> pd.DataFrame:
        """
        Get the processed exceptions dataframe

        :return: processed dataframe
        """
        return self.exceptions_df
