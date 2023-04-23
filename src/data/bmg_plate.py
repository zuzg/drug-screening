import os
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt


class Plate:
    """
    Class representing a plate with values resulting from an HTS experiment
    """
    def __init__(self, filepath: str) -> None:
        """
        :param filepath: path to the file consisting plate
        """
        self.filepath = filepath
        self.barcode = filepath.split('/')[-1].split('.')[0].split('\\')[-1]
        self.plate_array = self.parse_file()
        self.control_statistics()
        self.z_factor = 1 - (3*(self.std_pos+self.std_neg) /
                             (self.mean_neg-self.mean_pos))

    def parse_file(self) -> np.array:
        """
        Read data from txt file to np.array

        :return: array with plate values
        """
        plate = np.zeros(shape=(16, 24))
        with open(self.filepath) as f:
            for i, line in enumerate(f.readlines()):
                # handle different formatting (as in FIREFLY)
                if i == 0 and 'A' not in line:
                    df = pd.read_csv(self.filepath, header=None)
                    plate = df.to_numpy()
                    break
                well, value = line.split()
                i, j = self.well_to_ids(well)
                plate[i, j] = value
        return plate

    def well_to_ids(self, well_name: str) -> tuple[int, int]:
        """
        Helper method to map well name to index

        :param well_name: well name in format {letter}{number} (e.g. A10)
        to be transformed
        """
        head = well_name.rstrip('0123456789')
        tail = well_name[len(head):]
        return ord(head)-65, int(tail)-1

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
        # append to df then, add visualization
        ...

    def summary_row(self) -> list:
        """
        Get all features describing a plate in the form of a list

        :return: list consisting of plate features
        """
        return [self.barcode, self.plate_array,
                self.std_pos, self.std_neg,
                self.mean_pos, self.mean_neg,
                self.z_factor]


def parse_bmg_files_from_dir(dir: str) -> pd.DataFrame:
    """
    Parse file from directory with BMG files to DataFrame

    :param dir: directory consisting of BMG files
    :return: DataFrame with BMG files (=plates) as rows
    """
    df = pd.DataFrame(columns=['barcode', 'plate_array', 'std_pos', 'std_neg',
                               'mean_pos', 'mean_neg', 'z_factor'])
    df['plate_array'] = df['plate_array'].astype(object)
    for filename in os.listdir(dir):
        plate = Plate(os.path.join(dir, filename))
        df.loc[len(df)] = plate.summary_row()
    return df


def visualize_multiple_plates(df: pd.DataFrame) -> plt.Figure:
    """
    Visualize plate values on grid 3x3

    :param df: DataFrame with plates
    :return: plot with visualized plates
    """
    fig, axes = plt.subplots(3, 3, constrained_layout=True)
    for ax, plate, barcode in zip(axes.flat, df.plate_array, df.barcode):
        im = ax.pcolormesh(plate)
        ax.set_title(barcode, fontsize=9)
        ax.axis("off")
    fig.colorbar(im, ax=axes.ravel().tolist(), location='bottom', aspect=60)
    return fig
