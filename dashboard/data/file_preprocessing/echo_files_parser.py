from __future__ import annotations
import pandas as pd
import os


class EchoFilesParser:
    def __init__(
        self,
        echo_files_dir: str,
    ):
        """
        Parser for csv echo files.

        :param echo_files_dir: directory containing echo files
        """
        self.echo_files_dir = echo_files_dir

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

    def parse_file(self, filename: str) -> tuple[pd.DataFrame, pd.DataFrame]:
        """
        Preprocesses a csv echo file and stores it in a dataframe (exceptions separated).

        :param filename: path to the file
        :return: dataframe with echo data, dataframe with exceptions
        """
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
            exceptions_df = pd.read_csv(filename)
            echo_df = None

        if echo_df is not None:
            mask = (
                echo_df[echo_df.columns[0]]
                .astype(str)
                .str.lower()
                .str.startswith("instrument", na=False)
            )
            echo_df = echo_df[~mask]
        return echo_df, exceptions_df

    def parse_files_from_dir(self) -> EchoFilesParser:
        """
        Preprocesses csv echo files from a directory and stores them in dataframes (exceptions separated).

        :return: self
        """
        exception_dfs, echo_dfs = [], []
        for filename in os.listdir(self.echo_files_dir):
            if not (filename.endswith(".csv")):
                continue
            filepath = os.path.join(self.echo_files_dir, filename)
            echo_df, exceptions_df = self.parse_file(filepath)
            exception_dfs.append(exceptions_df)
            echo_dfs.append(echo_df)

        if echo_df is not None:
            self.echo_df = pd.concat(echo_dfs, ignore_index=True)
        self.exceptions_df = pd.concat(exception_dfs, ignore_index=True)

        return self

    def retain_key_columns(self, columns: list[str] = None) -> EchoFilesParser:
        """
        Retains only the specified columns.

        :param columns: list of columns to retain
        :return: self
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
