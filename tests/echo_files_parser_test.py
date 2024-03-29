import pandas as pd
from unittest.mock import mock_open, MagicMock, patch
from dashboard.data.file_preprocessing.echo_files_parser import EchoFilesParser
import io


def test_find_marker_rows():
    file_content = "Skip_this\n[EXCEPTIONS]\nline1\nline2\n[DETAILS]\nline3\n"
    with patch("builtins.open", mock_open(read_data=file_content)):
        parser = EchoFilesParser()
        markers = parser.find_marker_rows(
            io.StringIO(file_content), ("[EXCEPTIONS]", "[DETAILS]")
        )
        assert [1, 4] == markers


def test_parse_files():
    echo1_content = (
        "[DETAILS]\nPlate,Well,Transfer Volume\nplate123,A01,10\nInstrument\n"
    )

    parser = EchoFilesParser()
    parser.find_marker_rows = MagicMock(return_value=[0])

    with patch("builtins.open") as mock_file:
        mock_file.side_effect = [
            mock_open(read_data=echo1_content).return_value,
        ]
        parser.parse_files(tuple([["echo_file1.csv", io.StringIO(echo1_content)]]))
        echo_df = parser.echo_df
        expected_echo_df = pd.DataFrame(
            {
                "Plate": ["plate123"],
                "Well": ["A01"],
                "Transfer Volume": [10.0],
            }
        )
        pd.testing.assert_frame_equal(echo_df, expected_echo_df)


def test_retain_key_columns():
    echo1_content = (
        "[DETAILS]\nPlate,Well,Transfer Volume\nplate123,A01,10\nInstrument\n"
    )
    parser = EchoFilesParser()
    parser.find_marker_rows = MagicMock(return_value=[0])
    with patch("builtins.open", mock_open(read_data=echo1_content)):
        parser.parse_files(tuple([["echo_file1.csv", io.StringIO(echo1_content)]]))
        parser.exceptions_df = pd.DataFrame()
        parser.retain_key_columns(["Plate", "Wrong_column"])
        expected_echo_df = pd.DataFrame({"Plate": ["plate123"]})
        pd.testing.assert_frame_equal(parser.get_processed_echo_df(), expected_echo_df)
