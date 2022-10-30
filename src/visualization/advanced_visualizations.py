import matplotlib as plt
import pandas as pd
import seaborn as sns


def histogram_control_value(df: pd.DataFrame, feature: str, control_pos: str, control_neg: str) -> sns.displot:
    """
    Plot histogram for one dataset with positive and negative control values.
    """
    histogram = sns.histplot(df, x=df[feature], kde=True)
    histogram.vlines(df[control_neg], 0, 1300, colors='red', linestyles='dotted', label="negative")
    histogram.vlines(df[control_pos], 0, 1300, colors='green', linestyles='dotted', label='positive')
    histogram.set(title=f"Histogram for {feature} with control values")

    return histogram


def scatter_2d(df: pd.DataFrame, feature_x: str, feature_y: str) -> sns.scatterplot:
    """
    Plot histogram for two datasets.
    """
    scatter = sns.scatterplot(df, x=feature_x, y=feature_y, hue='Barcode_prefix')
    scatter.set(title=f"Scatter plot for {feature_x} and {feature_y}")

    return scatter
