import os
import numpy as np
import pandas as pd
from collections import namedtuple


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


def parse_bmg_file(filepath: str) -> tuple[str, np.ndarray]:
    """
    Read data from txt file to np.array

    :param filepath: path to the file with bmg plate
    :return: barcode and array with plate values
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


def parse_bmg_files_from_dir(dir: str) -> tuple[pd.DataFrame, np.ndarray]:
    """
    Parse file from directory with BMG files to DataFrame

    :param dir: directory consisting of BMG files
    :return: DataFrame with BMG files (=plates) as rows, array with plate values
    """
    plate_summaries = []
    plate_values = []
    for filename in os.listdir(dir):
        barcode, plate_array = parse_bmg_file(os.path.join(dir, filename))
        plate = Plate(barcode, plate_array)
        z_wo, outliers_mask = calculate_z_outliers(plate)
        plate_summaries.append(get_summary_tuple(plate, z_wo))
        plate_values.append([plate.plate_array, outliers_mask])

    df = pd.DataFrame(plate_summaries)
    plate_values = np.asarray(plate_values)
    return df, plate_values


def calculate_activation_inhibition_zscore(
    df_stats: pd.Series,
    values: np.ndarray,
    mode: str = "all",
    without_pos: bool = False,
) -> tuple[np.ndarray, np.ndarray]:
    """
    Calculates the activation and inhibition values for each well.
    :param df_stats: dataframe with pre-calculated statistics
    :param values: values to calculate activation/inhibition and an outlier mask
    :param mode: mode of calculation, either "all", "activation" or "inhibition"
    :param without_pos: whether to calculate without positive controls (in case of "activation" mode)
    """
    activation, inhibition = None, None
    if mode == "activation" or mode == "all":
        # NOTE: for now `without_pos` is not used
        if without_pos:
            activation = (values - df_stats["mean_neg"]) / (df_stats["mean_neg"]) * 100
        else:
            activation = (
                (values - df_stats["mean_neg"])
                / (df_stats["mean_pos"] - df_stats["mean_neg"])
                * 100
            )

    if mode == "inhibition" or mode == "all":
        inhibition = (
            1
            - ((values - df_stats["mean_pos"]))
            / (df_stats["mean_neg"] - df_stats["mean_pos"])
        ) * 100

    z_score = (values - df_stats["mean_cmpd"]) / df_stats["std_cmpd"]

    assert not (
        activation == inhibition
    ).all(), "Activation and inhibition are the same"
    return activation, inhibition, z_score


def get_activation_inhibition_dict(
    df_stats: pd.DataFrame, plate_values: np.ndarray, modes: list[str]
) -> dict[str, dict[str, float]]:
    """
    Calculates activation and inhibition for each compound in the plates.
    :param df_stats: dataframe with statistics for each plate
    :param plate_values: array with values in the plate
    :param mode: list of modes to calculate activation and inhibition
    :return: dictionary with activation and inhibition values for each compound in the plate
    """
    act_inh_dict = {}
    for (_, row_stats), v in zip(df_stats.iterrows(), plate_values):
        mode = modes[row_stats["barcode"]] if row_stats["barcode"] in modes else "all"
        activation, inhibition, z_score = calculate_activation_inhibition_zscore(
            row_stats, v[0], mode=mode
        )
        act_inh_dict[row_stats["barcode"]] = {
            "activation": activation,
            "inhibition": inhibition,
            "z_score": z_score,
            "outliers": v[1],
        }
    return act_inh_dict
