import numpy as np
import matplotlib.pyplot as plt


class Plate:
    def __init__(self, filename: str) -> None:
        self.filename = filename
        self.barcode = filename.split('/')[-1].split('.')[0]
        self.plate_array = self.parse_file()
        self.control_statistics()
        self.z = 1 - (3*(self.std_pos+self.std_neg)/(self.mean_neg-self.mean_pos))

    def parse_file(self) -> np.array:
        plate = np.zeros(shape=(16, 24))
        with open(self.filename) as f:
            for line in f.readlines():
                well, value = line.split()
                i, j = self.well_to_ids(well)
                plate[i, j] = value
        return plate

    def well_to_ids(self, well_name: str) -> tuple[int, int]:
        head = well_name.rstrip('0123456789')
        tail = well_name[len(head):]
        return ord(head)-65, int(tail)-1

    def control_statistics(self) -> None:
        pos = self.plate_array[:, 22]
        neg = self.plate_array[:, 23]
        self.std_pos = np.std(pos)
        self.std_neg = np.std(neg)
        self.mean_pos = np.mean(pos)
        self.mean_neg = np.mean(neg)

    def visualize_plate(self) -> plt.Figure:
        fig = plt.figure()
        ax = fig.add_subplot(1, 1, 1)
        im = ax.imshow(self.plate_array, cmap='viridis')
        ax.set_xticklabels([0, 1, 6, 11, 16, 21])
        ax.set_yticklabels([0, 'A', 'C', 'D', 'F', 'H', 'J', 'L', 'N'])
        ax.set_title(self.barcode)
        fig.colorbar(im)
        return fig
