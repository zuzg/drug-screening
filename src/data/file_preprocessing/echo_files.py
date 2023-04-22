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
        self.echo_df = pd.DataFrame()
        self.exceptions_df = pd.DataFrame()

    def find_row_numbers(self, file:str, markers:tuple[str]) -> list[int]:
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
        if len(markers_rows) == 0:
            raise ValueError('No marker found in file.')
        return markers_rows

    def parse_files(self) -> EchoFilesParser:
        """
        Preprocesses csv echo files, splits regular records from exceptions.
        """
        if not(all(file.endswith('.csv') for file in self.echo_files)):
            raise ValueError(f"Expected files to be of '*.csv' type, provided: {self.echo_files}")

        for filename in self.echo_files: 
            exceptions_line, details_line = self.find_row_numbers(filename, ('[EXCEPTIONS]', '[DETAILS]'))
            exceptions_df = pd.read_csv(filename, skiprows=exceptions_line+1, nrows=(details_line-1)-exceptions_line-2)
            echo_df = pd.read_csv(filename, skiprows=details_line+1)
            echo_df = echo_df[~echo_df[echo_df.columns[0]].str.startswith('Instrument')]

            self.exceptions_df = exceptions_df if self.exceptions_df.empty else pd.concat([self.exceptions_df, exceptions_df])
            self.echo_df = echo_df if self.echo_df.empty else pd.concat([self.echo_df, echo_df])

        return self
    
    def link_bmg_files(self, bmg_files: list[str]) -> EchoFilesParser:
        """
        Links bmg files to the echo files.

        :param bmg_files: list of bmg files
        """
        #
        # for bmg_file in bmg_files:
        # TODO: link values from bmg files to echo files + write tests
        #
        return self

    def retain_columns(self, columns: list[str]) -> EchoFilesParser:
        """
        Retains only the specified columns.

        :param columns: list of columns to retain
        """
        self.echo_df = self.echo_df[columns]
        self.exceptions_df = self.exceptions_df[columns]
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