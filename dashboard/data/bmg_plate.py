import io
import numpy as np
import pandas as pd
import logging

from collections import namedtuple
from enum import Enum, auto

logger = logging.getLogger(__name__)


PlateSummary = namedtuple(
    "PlateSummary",
    [
        "barcode",
        "std_cmpd",
        "std_pos",
        "std_neg",
        "mean_cmpd",
        "mean_pos",
        "mean_neg",
        "z_factor",
        "z_factor_no_outliers",
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


def find_outliers(
    control: np.ndarray, control_std: float, control_mean: float
) -> tuple:
    """
    Find outliers (max 2) in a given control array and assign them value of NaN.
    The method is using standard deviation. In case of finding more than 2 outliers,
    remove the most outling ones.

    :param control: array containing control values (pos or neg)
    :param control_mean: mean of given control array
    :param control_std: std of given control array
    :return: outliers indices
    """
    cut_off = 3 * control_std
    lower_limit = control_mean - cut_off
    upper_limit = control_mean + cut_off
    all_outliers = np.where((control > upper_limit) | (control < lower_limit))[0]
    if len(all_outliers) == 0:
        return None
    outliers = list(
        set(np.argsort(np.abs(control - control_mean))[-2:]) & set(all_outliers)
    )
    return outliers


def calculate_z_outliers(plate: Plate) -> tuple[float, np.ndarray]:
    """
    Method to update controls after finding outliers

    :param plate: Plate object
    :return: z factor after removing outliers, outliers mask
    """
    std_pos, std_neg, mean_pos, mean_neg, _ = control_statistics(plate.pos, plate.neg)
    outliers_pos = find_outliers(plate.pos, std_pos, mean_pos)
    outliers_neg = find_outliers(plate.neg, std_neg, mean_neg)
    new_pos = plate.pos.copy()
    new_neg = plate.neg.copy()
    outliers_mask = np.zeros(shape=plate.plate_array.shape)
    if outliers_pos:
        new_pos[outliers_pos] = np.nan
        outliers_mask[outliers_pos, -1] = 1
    if outliers_neg:
        new_neg[outliers_neg] = np.nan
        outliers_mask[outliers_neg, -2] = 1
    _, _, _, _, z_factor_wo = control_statistics(new_pos, new_neg)
    return z_factor_wo, outliers_mask


def get_summary_tuple(plate: Plate, z_factor_wo: float) -> PlateSummary:
    """
    Get all features describing a plate in the form of a namedtuple

    :param plate: Plate object to be summarized
    :param z_factor_wo: z_factor calculated after removing outliers
    :return: namedtuple consisting of plate features
    """
    std_pos, std_neg, mean_pos, mean_neg, z_factor = control_statistics(
        plate.pos, plate.neg
    )

    std_cmpd = np.nanstd(plate.plate_array[:, :22])
    mean_cmpd = np.nanmean(plate.plate_array[:, :22])

    plate_summary = PlateSummary(
        plate.barcode,
        std_cmpd,
        std_pos,
        std_neg,
        mean_cmpd,
        mean_pos,
        mean_neg,
        z_factor,
        z_factor_wo,
    )
    return plate_summary


def well_to_ids(well_name: str) -> tuple[int, int]:
    """
    Helper method to map well name to index

    :param well_name: well name in format {letter}{number} (e.g. A10)
    to be transformed
    :return: well name as indices
    """
    head = well_name.rstrip("0123456789")
    tail = well_name[len(head) :]
    return ord(head) - 65, int(tail) - 1


def parse_bmg_file(filename: str, filecontent: io.StringIO) -> np.ndarray:
    """
    Read data from iostring file to np.array

    :param filename: name of file needed to extract barcode
    :param filecontent: content of file
    :return: array with plate values
    """
    plate = np.zeros(shape=(16, 24))
    barcode = filename.split(".")[0].split("\\")[-1]
    for i, line in enumerate(filecontent):
        # handle different formatting (as in FIREFLY)
        if i == 0 and "A" not in line:
            df = pd.read_csv(filecontent, header=None)
            plate = df.to_numpy()
            break
        if not line.strip():
            continue
        cells = line.split()
        if len(cells) != 2:
            raise ValueError(
                f"Wrong format of file {filename} - line {i} has {len(cells)} cells instead of 2"
            )
        well, value = cells
        i, j = well_to_ids(well)
        plate[i, j] = value
    return barcode, plate


def parse_bmg_files(
    files: tuple[str, io.StringIO]
) -> tuple[pd.DataFrame, np.ndarray, dict[str, str]]:
    """
    Parse file from iostring with BMG files to DataFrame

    :param files: tuple containing names and content of files
    :param failed_files: dictionary with failed files
    :return: DataFrame with BMG files (=plates) as rows,
        plates values as np.array and failed files with errors
    """
    plate_summaries = []
    plate_values = []
    failed_files = {}
    for filename, filecontent in files:
        try:
            barcode, plate_array = parse_bmg_file(filename, filecontent)
            plate = Plate(barcode, plate_array)
            z_wo, outliers_mask = calculate_z_outliers(plate)
            plate_summaries.append(get_summary_tuple(plate, z_wo))
            plate_values.append([plate.plate_array, outliers_mask])
        except Exception as e:
            logger.warning(f"Error while parsing file {filename}: {e}")
            failed_files[filename] = str(e)
    df = pd.DataFrame(plate_summaries)
    plate_values = np.asarray(plate_values)
    return df, plate_values, failed_files


def calculate_activation_inhibition_zscore(
    values: np.ndarray,
    stats: dict,
    mode: str,
    without_pos: bool = False,
) -> tuple[np.ndarray]:
    """
    Calculates the activation and inhibition values for each well.

    :param values: values to calculate activation/inhibition and an outlier mask
    :param stats: dictionary with statistics for all data
    :param mode: mode of calculation, either "all", "activation" or "inhibition"
    :param without_pos: whether to calculate without positive controls (in case of "activation" mode)
    :return: activation, inhibition and z-score values
    """
    activation, inhibition = None, None
    if mode == "activation":
        if without_pos:
            activation = (values - stats["mean_neg"]) / (stats["mean_neg"]) * 100
        else:
            activation = (
                (values - stats["mean_neg"])
                / (stats["mean_pos"] - stats["mean_neg"])
                * 100
            )

    if mode == "inhibition":
        inhibition = (
            (values - stats["mean_neg"]) / (stats["mean_pos"] - stats["mean_neg"]) * 100
        )

    z_score = (values - stats["mean_cmpd"]) / stats["std_cmpd"]

    return activation, inhibition, z_score


def get_activation_inhibition_zscore_dict(
    df_stats: pd.DataFrame,
    plate_values: np.ndarray,
    mode: str,
    without_pos: bool = False,
) -> dict[str, dict[str, float]]:
    """
    Calculates activation and inhibition for each compound in the plates.

    :param df_stats: dataframe with statistics for each plate
    :param plate_values: array with values in the plate
    :param mode: mode to calculate activation and inhibition
    :return: dictionary with activation and inhibition values for each compound in the plate
    """
    stats = {}
    all_compound_values = plate_values[:, 0, :, :22]
    all_control_pos_values = plate_values[:, 0, :, -1]
    all_control_neg_values = plate_values[:, 0, :, -2]

    stats["mean_cmpd"] = np.nanmean(all_compound_values)
    stats["std_cmpd"] = np.nanstd(all_compound_values)
    stats["mean_pos"] = np.nanmean(all_control_pos_values)
    stats["mean_neg"] = np.nanmean(all_control_neg_values)

    act_inh_dict = {}
    for (_, row_stats), v in zip(df_stats.iterrows(), plate_values):
        activation, inhibition, z_score = calculate_activation_inhibition_zscore(
            v[0], stats, mode, without_pos
        )
        act_inh_dict[row_stats["barcode"]] = {
            "activation": activation,
            "inhibition": inhibition,
            "z_score": z_score,
            "outliers": v[1],
        }
    return act_inh_dict


def filter_low_quality_plates(
    df: pd.DataFrame, plate_array: np.ndarray, threshold: float = 0.5
) -> tuple[pd.DataFrame, pd.DataFrame, np.ndarray]:
    """
    Remove plates with Z factor lower than threshold

    :param df: DataFrame with control values
    :param plate_array: array with plate values
    :param threshold: Z factor threshold value
    :return: high quality plates, low quality plates, high quality plate array
    """
    quality_mask = df.z_factor > threshold
    quality_df = df[quality_mask]
    low_quality_df = df[~quality_mask][["barcode", "z_factor"]]
    low_quality_ids = np.where(quality_mask == False)
    quality_plates = np.delete(plate_array, low_quality_ids, axis=0)
    return quality_df, low_quality_df, quality_plates
