from __future__ import annotations

import io

import pandas as pd


class EchoFilesParser:
    def __init__(
        self,
    ):
        """
        Parser for csv echo files.
        """
        self.echo_df = None
        self.exceptions_df = None

    def find_marker_rows(self, file: str, markers: tuple[str]) -> list[int]:
        """
        Finds the row numbers of marker lines in a ioString file.

        :param file: file to search
        :param markers: markers to search for
        """
        markers_rows = list()
        for i, line in enumerate(file):
            if line.strip() in markers:
                markers_rows.append(i)
            if len(markers_rows) == len(markers):
                return markers_rows
        return markers_rows

    def parse_files(self, echo_files: tuple[str, io.StringIO]) -> EchoFilesParser:
        """
        Preprocesses echo ioString files (csv form), splits regular records from exceptions.

        :param echo_files: tuple with filenames and filecontets
        :return self
        """
        exception_dfs, echo_dfs = [], []
        for filename, filecontent in echo_files:
            markers = self.find_marker_rows(filecontent, ("[EXCEPTIONS]", "[DETAILS]"))
            filecontent.seek(0)
            if len(markers) == 2:
                exceptions_line, details_line = markers
                exceptions_df = pd.read_csv(
                    filecontent,
                    skiprows=exceptions_line + 1,
                    nrows=(details_line - 1) - exceptions_line - 2,
                )
                filecontent.seek(0)
                echo_df = pd.read_csv(filecontent, skiprows=details_line + 1)
            elif len(markers) == 1:
                exceptions_df = pd.DataFrame()
                echo_df = pd.read_csv(filecontent, skiprows=markers[0] + 1)
            else:
                echo_df = pd.read_csv(filecontent)
                exceptions_df = pd.DataFrame()

            if echo_df is not None:
                mask = (
                    echo_df[echo_df.columns[0]]
                    .astype(str)
                    .str.lower()
                    .str.startswith("instrument", na=False)
                )
                echo_df = echo_df[~mask]
                echo_df = echo_df[~echo_df[echo_df.columns[0]].isin([""])]
            exception_dfs.append(exceptions_df)
            echo_dfs.append(echo_df)

        if echo_dfs:
            self.echo_df = pd.concat(echo_dfs, ignore_index=True)
        if exception_dfs:
            self.exceptions_df = pd.concat(exception_dfs, ignore_index=True)

        return self

    def merge_eos(self, eos_df: pd.DataFrame) -> int:
        """
        Merge echo df with eos df by plate and well

        :param eos_df: dataframe with eos, plate and well
        :return: number of skipped rows (without EOS)
        """
        # handle different well naming (A01 or A1)
        eos_df["Well"] = eos_df["Well"].str.replace(r"0(?!$)", "", regex=True)
        self.echo_df["Source Well"] = self.echo_df["Source Well"].str.replace(
            r"0(?!$)", "", regex=True
        )

        left_cols = ["Source Plate Barcode", "Source Well"]
        right_cols = ["Plate", "Well"]
        merged_df = pd.merge(
            self.echo_df, eos_df, how="left", left_on=left_cols, right_on=right_cols
        )
        no_eos = merged_df["EOS"].isna()
        merged_df = merged_df[~no_eos]
        self.echo_df = merged_df
        return len(no_eos)

    def retain_key_columns(self, columns: list[str] = None) -> EchoFilesParser:
        """
        Retains only the specified columns.

        :param columns: list of columns to retain
        :return: self
        """

        if columns is None:
            columns = [
                "EOS",
                "Source Plate Barcode",
                "Source Well",
                "Destination Plate Barcode",
                "Destination Well",
                "Actual Volume",
            ]

        retain_echo = [col for col in columns if col in self.echo_df.columns]
        self.echo_df = self.echo_df[retain_echo]
        if "Destination Well" in self.echo_df.columns:
            self.echo_df["Destination Well"] = self.echo_df[
                "Destination Well"
            ].str.replace(r"0(?!$)", "", regex=True)
        retain_exceptions = [
            col
            for col in columns + ["Transfer Status"]
            if col in self.exceptions_df.columns
        ]
        self.exceptions_df = self.exceptions_df[retain_exceptions]
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
