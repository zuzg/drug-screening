import os
import numpy as np
import pandas as pd
from collections import namedtuple


PlateSummary = namedtuple(
    "PlateSummary",
    [
        "barcode",
        "plate_array",
        "std_pos",
        "std_neg",
        "mean_pos",
        "mean_neg",
        "z_factor",
        "z_factor_no_outliers",
        "outliers_pos",
        "outliers_neg",
    ],
)


class Plate:
    """
    Class representing a plate with values resulting from an HTS experiment
    """

    def __init__(self, barcode: str, plate_array: np.ndarray) -> None:
        """
        :param filepath: path to the file consisting plate
        """
        self.barcode = barcode
        self.plate_array = plate_array
        self.pos = self.plate_array[:, -2]
        self.neg = self.plate_array[:, -1]
        (
            self.std_pos,
            self.std_neg,
            self.mean_pos,
            self.mean_neg,
            self.z_factor,
        ) = self.control_statistics(self.pos, self.neg)
        self.pos_wo, self.outliers_pos = self.find_outliers(
            self.pos, self.mean_pos, self.std_pos
        )
        self.neg_wo, self.outliers_neg = self.find_outliers(
            self.neg, self.mean_neg, self.std_neg
        )
        (
            self.std_pos_wo,
            self.std_neg_wo,
            self.mean_pos_wo,
            self.mean_neg_wo,
            self.z_factor_wo,
        ) = self.control_statistics(self.pos_wo, self.neg_wo)

    def control_statistics(self, pos: np.ndarray, neg: np.ndarray) -> tuple:
        """
        Calculate statistic for control values e.g. two last columns of a plate
        """
        std_pos = np.nanstd(pos)
        std_neg = np.nanstd(neg)
        mean_pos = np.nanmean(pos)
        mean_neg = np.nanmean(neg)
        z_factor = 1 - (3 * (std_pos + std_neg) / (mean_neg - mean_pos))
        return std_pos, std_neg, mean_pos, mean_neg, z_factor

    def find_outliers(
        self, control: np.ndarray, control_mean: float, control_std: float
    ) -> tuple:
        """
        Find outliers (max 2) in a given control array and assign them value of NaN.
        The method is using standard deviation: 3sigma rule

        :param control: array containing control values (pos or neg)
        :param control_mean: mean of given control array
        :param control_std: std of given control array
        :return: control array with outliers replaced to NaNs, tuple with outliers indices and values
        """
        cut_off = 3 * control_std
        lower_limit = control_mean - cut_off
        upper_limit = control_mean + cut_off
        outliers = np.where((control > upper_limit) | (control < lower_limit))[0]
        if len(outliers) == 0:
            return control, [np.nan]
        elif len(outliers) > 2:
            while len(outliers) > 2:
                max_o = np.max(outliers)
                min_o = np.min(outliers)
                if max_o - upper_limit > lower_limit - min_o:
                    outliers = outliers[outliers != max_o]
                else:
                    outliers = outliers[outliers != min_o]
        new_control = control.copy()
        new_control[outliers] = np.nan
        outliers_values = control[outliers]
        return new_control, (outliers, outliers_values)

    def get_summary_tuple(self) -> PlateSummary:
        """
        Get all features describing a plate in the form of a namedtuple

        :param plate: Plate object to be summarized
        :return: namedtuple consisting of plate features
        """
        plate_summary = PlateSummary(
            self.barcode,
            self.plate_array,
            self.std_pos,
            self.std_neg,
            self.mean_pos,
            self.mean_neg,
            self.z_factor,
            self.z_factor_wo,
            self.outliers_pos,
            self.outliers_neg,
        )
        return plate_summary


def well_to_ids(well_name: str) -> tuple[int, int]:
    """
    Helper method to map well name to index

    :param well_name: well name in format {letter}{number} (e.g. A10)
    to be transformed
    """
    head = well_name.rstrip("0123456789")
    tail = well_name[len(head) :]
    return ord(head) - 65, int(tail) - 1


def parse_bmg_file(filepath: str) -> np.array:
    """
    Read data from txt file to np.array

    :return: array with plate values
    """
    plate = np.zeros(shape=(16, 24))
    barcode = filepath.split("/")[-1].split(".")[0].split("\\")[-1]
    with open(filepath) as f:
        for i, line in enumerate(f.readlines()):
            # handle different formatting (as in FIREFLY)
            if i == 0 and "A" not in line:
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
