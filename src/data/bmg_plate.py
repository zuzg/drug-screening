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
        :param barcode: barcode identifying plate
        :param plate_array: array consisting plate values
        """
        self.barcode = barcode
        self.plate_array = plate_array.astype(np.float32)
        self.pos = self.plate_array[:, -1]
        self.neg = self.plate_array[:, -2]


def control_statistics(pos: np.ndarray, neg: np.ndarray) -> tuple:
    """
    Calculate statistic for control values e.g. two last columns of a plate

    :param pos: array with positive control
    :param neg: array with negative control
    :return: standard deviation and mean of controls, z factor
    """
    std_pos = np.nanstd(pos)
    std_neg = np.nanstd(neg)
    mean_pos = np.nanmean(pos)
    mean_neg = np.nanmean(neg)
    z_factor = 1 - (3 * (std_pos + std_neg) / (mean_neg - mean_pos))
    return std_pos, std_neg, mean_pos, mean_neg, z_factor


def remove_outliers(
    control: np.ndarray, control_std: float, control_mean: float
) -> tuple:
    """
    Find outliers (max 2) in a given control array and assign them value of NaN.
    The method is using standard deviation. In case of finding more than 2 outliers,
    remove the most outling ones.

    :param control: array containing control values (pos or neg)
    :param control_mean: mean of given control array
    :param control_std: std of given control array
    :return: control with outliers as nans, outliers indices
    """
    cut_off = 3 * control_std
    lower_limit = control_mean - cut_off
    upper_limit = control_mean + cut_off
    all_outliers = np.where((control > upper_limit) | (control < lower_limit))[0]
    if len(all_outliers) == 0:
        return control, np.nan
    outliers = set(np.argsort(np.abs(control - control_mean))[-2:]) & set(all_outliers)
    new_control = control.copy()
    return new_control, outliers


def get_summary_tuple(plate: Plate) -> PlateSummary:
    """
    Get all features describing a plate in the form of a namedtuple

    :param plate: Plate object to be summarized
    :return: namedtuple consisting of plate features
    """
    std_pos, std_neg, mean_pos, mean_neg, z_factor = control_statistics(
        plate.pos, plate.neg
    )
    new_pos, outliers_pos = remove_outliers(plate.pos, std_pos, mean_pos)
    new_neg, outliers_neg = remove_outliers(plate.neg, std_neg, mean_neg)
    _, _, _, _, z_factor_wo = control_statistics(new_pos, new_neg)

    plate_summary = PlateSummary(
        plate.barcode,
        plate.plate_array,
        std_pos,
        std_neg,
        mean_pos,
        mean_neg,
        z_factor,
        z_factor_wo,
        outliers_pos,
        outliers_neg,
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
        plates_list.append(get_summary_tuple(plate))
    df = pd.DataFrame(plates_list)
    return df
