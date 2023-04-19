import os
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt


class Plate:
    def __init__(self, filepath: str) -> None:
        self.filepath = filepath
        self.barcode = filepath.split('/')[-1].split('.')[0].split('\\')[-1]
        self.plate_array = self.parse_file()
        self.control_statistics()
        self.z = 1 - (3*(self.std_pos+self.std_neg) /
                      (self.mean_neg-self.mean_pos))

    def parse_file(self) -> np.array:
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
        head = well_name.rstrip('0123456789')
        tail = well_name[len(head):]
        return ord(head)-65, int(tail)-1

    def control_statistics(self) -> None:
        pos = self.plate_array[:, -2]
        neg = self.plate_array[:, -1]
        self.std_pos = np.std(pos)
        self.std_neg = np.std(neg)
        self.mean_pos = np.mean(pos)
        self.mean_neg = np.mean(neg)

    def find_outliers(self):
        # TODO
        # append to df then (well + value?)
        ...

    def summary_row(self) -> list:
        return [self.barcode, self.plate_array,
                self.std_pos, self.std_neg,
                self.mean_pos, self.mean_neg,
                self.z]


def parse_bmg_files_from_dir(dir: str) -> pd.DataFrame:
    df = pd.DataFrame(columns=['barcode', 'plate_array',
                      'std_pos', 'std_neg', 'mean_pos', 'mean_neg', 'z'])
    df['plate_array'] = df['plate_array'].astype(object)
    for filename in os.listdir(dir):
        plate = Plate(os.path.join(dir, filename))
        df.loc[len(df)] = plate.summary_row()
    return df


def visualize_plate(plate_array: np.array, barcode: str) -> plt.Figure:
    fig = plt.figure()
    ax = fig.add_subplot(1, 1, 1)
    im = ax.imshow(plate_array, cmap='viridis')
    ax.set_xticklabels([0, 1, 6, 11, 16, 21])
    ax.set_yticklabels([0, 'A', 'C', 'D', 'F', 'H', 'J', 'L', 'N'])
    ax.set_title(barcode)
    fig.colorbar(im)
    return fig
