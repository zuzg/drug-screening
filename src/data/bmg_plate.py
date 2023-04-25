import os
import numpy as np
import pandas as pd
from collections import namedtuple


PlateSummary = namedtuple('PlateSummary', ['barcode', 'plate_array',
                                           'std_pos', 'std_neg',
                                           'mean_pos', 'mean_neg',
                                           'z_factor'])


class Plate:
    """
    Class representing a plate with values resulting from an HTS experiment
    """

    def __init__(self, barcode: str, plate_array: np.array) -> None:
        """
        :param filepath: path to the file consisting plate
        """
        self.barcode = barcode
        self.plate_array = plate_array
        self.control_statistics()
        self.z_factor = 1 - (3*(self.std_pos+self.std_neg) /
                             (self.mean_neg-self.mean_pos))

    def control_statistics(self) -> None:
        """
        Calculate statistic for control values e.g. two last columns of a plate
        """
        pos = self.plate_array[:, -2]
        neg = self.plate_array[:, -1]
        self.std_pos = np.std(pos)
        self.std_neg = np.std(neg)
        self.mean_pos = np.mean(pos)
        self.mean_neg = np.mean(neg)

    def find_outliers(self):
        # TODO
        ...

    def get_summary_tuple(self) -> PlateSummary:
        """
        Get all features describing a plate in the form of a namedtuple

        :param plate: Plate object to be summarized
        :return: namedtuple consisting of plate features
        """
        plate_summary = PlateSummary(self.barcode, self.plate_array,
                                     self.std_pos, self.std_neg,
                                     self.mean_pos, self.mean_neg,
                                     self.z_factor)
        return plate_summary


def well_to_ids(well_name: str) -> tuple[int, int]:
    """
    Helper method to map well name to index

    :param well_name: well name in format {letter}{number} (e.g. A10)
    to be transformed
    """
    head = well_name.rstrip('0123456789')
    tail = well_name[len(head):]
    return ord(head)-65, int(tail)-1


def parse_bmg_file(filepath: str) -> np.array:
    """
    Read data from txt file to np.array

    :return: array with plate values
    """
    plate = np.zeros(shape=(16, 24))
    barcode = filepath.split('/')[-1].split('.')[0].split('\\')[-1]
    with open(filepath) as f:
        for i, line in enumerate(f.readlines()):
            # handle different formatting (as in FIREFLY)
            if i == 0 and 'A' not in line:
                df = pd.read_csv(filepath, header=None)
                plate = df.to_numpy()
                break
            well, value = line.split()
            i, j = well_to_ids(well)
            plate[i, j] = value
    return barcode, plate


def parse_bmg_files_from_dir(dir: str) -> pd.DataFrame:
    """
    Parse file from directory with BMG files to DataFrame

    :param dir: directory consisting of BMG files
    :return: DataFrame with BMG files (=plates) as rows
    """
    plates_list = []
    for filename in os.listdir(dir):
        barcode, plate_array = parse_bmg_file(os.path.join(dir, filename))
        plate = Plate(barcode, plate_array)
        plates_list.append(plate.get_summary_tuple())
    df = pd.DataFrame(plates_list)
    return df
