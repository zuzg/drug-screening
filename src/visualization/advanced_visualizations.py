import numpy as np
import matplotlib.pyplot as plt
import pandas as pd
import seaborn as sns


def histogram_control_value(df: pd.DataFrame, feature: str, control_pos: str, control_neg: str) -> sns.displot:
    """
    Plot histogram for one dataset with positive and negative control values.

    :param df: DataFrame to be visualized

    :param feature: name of column to be visualized

    :param control_pos: name of positive control feature

    :param control_neg: name of negative control feature

    :return: distribution plot for the passed feature and control values
    """
    histogram = sns.histplot(df, x=df[feature], kde=True)
    histogram.vlines(df[control_neg], 0, 1300, colors='red',
                     linestyles='dotted', label="negative")
    histogram.vlines(df[control_pos], 0, 1300, colors='green',
                     linestyles='dotted', label='positive')
    histogram.set(title=f"Histogram for {feature} with control values")

    return histogram


def scatter_2d(df: pd.DataFrame, feature_x: str, feature_y: str) -> sns.scatterplot:
    """
    Plot histogram for two datasets.

    :param df: DataFrame to be visualized

    :param feature_x: name of feature for x-axis

    :param feature_y: name of feature for y-axis

    :return: scatter plot for the passed data
    """
    scatter = sns.scatterplot(
        df, x=feature_x, y=feature_y, hue='Barcode_prefix')
    scatter.set(title=f"Scatter plot for {feature_x} and {feature_y}")

    return scatter


def plot_umap(X_umap: np.ndarray, y: np.ndarray) -> None:
    """
    Show scatter plot for the UMAP data

    :param X_umap: DataFrame to be visualized

    :param y: name of feature for x-axis

    :return: scatter plot for UMAP
    """
    plt.scatter(
        X_umap[:, 0],
        X_umap[:, 1],
        c=y, cmap='Spectral', s=5)
    plt.gca().set_aspect('equal', 'datalim')
    plt.title('UMAP projection of assays', fontsize=16)
    plt.show()
