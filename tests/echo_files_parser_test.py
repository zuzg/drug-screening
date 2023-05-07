import pandas as pd
from unittest.mock import mock_open, MagicMock, patch
from src.data.file_preprocessing.echo_files_parser import EchoFilesParser


def test_find_marker_rows():
    file_content = "Skip_this\n[EXCEPTIONS]\nline1\nline2\n[DETAILS]\nline3\n"
    with patch("builtins.open", mock_open(read_data=file_content)):
        parser = EchoFilesParser(["test_file.csv"])
        markers = parser.find_marker_rows(
            "test_file.csv", ("[EXCEPTIONS]", "[DETAILS]")
        )
        assert markers == [1, 4]


def test_parse_files():
    echo1_content = (
        "[DETAILS]\nPlate,Well,Transfer Volume\nplate123,A01,10\nInstrument\n"
    )
    echo2_content = "[DETAILS]\nPlate,Well,Transfer Volume\nplate456,B01,20\nInstrument\nInstrument\n"
    parser = EchoFilesParser(["echo_file1.csv", "echo_file2.csv"])
    parser.find_marker_rows = MagicMock(return_value=[0])

    with patch("builtins.open") as mock_file:
        mock_file.side_effect = [
            mock_open(read_data=echo1_content).return_value,
            mock_open(read_data=echo2_content).return_value,
        ]
        parser.parse_files()
        expected_echo_df = pd.DataFrame(
            {
                "Plate": ["plate123", "plate456"],
                "Well": ["A01", "B01"],
                "Transfer Volume": [10.0, 20.0],
            }
        )
        pd.testing.assert_frame_equal(parser.get_processed_echo_df(), expected_echo_df)


def test_retain_key_columns():
    echo1_content = (
        "[DETAILS]\nPlate,Well,Transfer Volume\nplate123,A01,10\nInstrument\n"
    )
    parser = EchoFilesParser(["echo_file1.csv"])
    parser.find_marker_rows = MagicMock(return_value=[0])
    with patch("builtins.open", mock_open(read_data=echo1_content)):
        parser.parse_files()
        parser.retain_key_columns(["Plate", "Wrong_column"])
        expected_echo_df = pd.DataFrame({"Plate": ["plate123"]})
        pd.testing.assert_frame_equal(parser.get_processed_echo_df(), expected_echo_df)
