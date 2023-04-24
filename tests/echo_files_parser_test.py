import pandas as pd
from unittest.mock import mock_open, MagicMock, patch
from src.data.file_preprocessing.echo_files_parser import EchoFilesParser


def test_find_marker_rows():
    file_content = 'Skip_this\n[EXCEPTIONS]\nline1\nline2\n[DETAILS]\nline3\n'
    with patch('builtins.open', mock_open(read_data=file_content)):
        parser = EchoFilesParser(['test_file.csv'])
        markers = parser.find_marker_rows('test_file.csv', ('[EXCEPTIONS]', '[DETAILS]'))
        assert markers == [1, 4]


def test_parse_files():
    echo1_content = '[DETAILS]\nPlate,Well,Transfer Volume\nplate123,A01,10\nInstrument\n'
    echo2_content = '[DETAILS]\nPlate,Well,Transfer Volume\nplate456,B01,20\nInstrument\nInstrument\n'
    parser = EchoFilesParser(['echo_file1.csv', 'echo_file2.csv'])
    parser.find_marker_rows = MagicMock(return_value=[0])

    with patch('builtins.open') as mock_file:
        mock_file.side_effect = [
            mock_open(read_data=echo1_content).return_value,
            mock_open(read_data=echo2_content).return_value,
        ]
        parser.parse_files()
        expected_echo_df = pd.DataFrame({'Plate': ['plate123','plate456'], 'Well': ['A01','B01'], 'Transfer Volume': [10.0, 20.0]})
        pd.testing.assert_frame_equal(parser.get_processed_echo_df(), expected_echo_df)


def test_link_bmg_files():
    echo1_content = '[DETAILS]\nDestination Plate Barcode,Destination Well\nPLATE_BARCODE,A01\nPLATE_BARCODE,A02\n'
    echo2_content = '[DETAILS]\nDestination Plate Barcode,Destination Well\nPLATE_BARCODE,B01\nPLATE_BARCODE2,B02\nInstrument\n'
    bmg1_content = 'A01\t10\nA02\t20\nA03\t30\nA04\t40\n'
    bmg2_content = 'B01\t50\nB02\t60\nB03\t70\nB04\t80\n'
    parser = EchoFilesParser(['echo_file1.csv', 'echo_file2.csv'])
    parser.find_marker_rows = MagicMock(return_value=[0])

    with patch('builtins.open') as mock_file:
        mock_file.side_effect = [
            mock_open(read_data=echo1_content).return_value,
            mock_open(read_data=echo2_content).return_value,
            mock_open(read_data=bmg1_content).return_value,
            mock_open(read_data=bmg2_content).return_value, 'Destination Well', 'Value', 'Destination Plate Barcode'
        ]
        parser.parse_files()
        parser.link_bmg_files(['PLATE_BARCODE.txt', 'PLATE_BARCODE2.txt'], bmg_columns=['Well', 'Value'], bmg_keys=['Plate_barcode', 'Well'])\
            .retain_columns(['Destination Plate Barcode', 'Destination Well', 'Value'])
        expected_echo_df = pd.DataFrame({'Value': [10, 20, 60],
                                         'Destination Plate Barcode': ['PLATE_BARCODE','PLATE_BARCODE','PLATE_BARCODE2'],
                                         'Destination Well': ['A01', 'A02', 'B02'],})
        res_df = parser.get_processed_echo_df()
        cols = ['Destination Plate Barcode', 'Value', 'Destination Well']
        pd.testing.assert_frame_equal(res_df[cols], expected_echo_df[cols])


def test_retain_columns():
    echo1_content = '[DETAILS]\nPlate,Well,Transfer Volume\nplate123,A01,10\nInstrument\n'
    parser = EchoFilesParser(['echo_file1.csv'])
    parser.find_marker_rows = MagicMock(return_value=[0])
    with patch('builtins.open', mock_open(read_data=echo1_content)):
        parser.parse_files()
        parser.retain_columns(['Plate', 'Wrong_column'])
        expected_echo_df = pd.DataFrame({'Plate': ['plate123']})
        pd.testing.assert_frame_equal(parser.get_processed_echo_df(), expected_echo_df)
