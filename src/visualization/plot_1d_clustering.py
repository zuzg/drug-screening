import matplotlib.pyplot as plt
import numpy as np

# it return plot ready to show, x are data in form of lists of list where each list is one cluster, lines is for making vertical lines on plot
def clustering_1D_visualization(x, lines=[]):

    # create scatterplot
    for i in range(len(x)):
        plt.scatter(x[i], np.zeros(np.shape(x[i])), label="cluster " + str(i))
    plt.legend()

    # hide y-axis
    ax = plt.gca()
    ax.get_yaxis().set_visible(False)

    # show vertical lines, if lines is given then use it if not make lines from average of border points
    if len(lines) > 0:
        for i in lines:
            plt.vlines(i, -1, 1)
    else:
        for i in range(len(x) - 1):
            plt.vlines((x[i][-1] + x[i + 1][0]) / 2, -1, 1)
    return plt
