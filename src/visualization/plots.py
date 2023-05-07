import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import plotly.express as px
import plotly.graph_objects as go


def plot_projection_2d(
    df: pd.DataFrame,
    feature: str,
    projection: str = "umap",
    width: int = 800,
    height: int = 600,
) -> go.Figure:
    """
    Plot selected projection and colour points with respect to selected feature.

    :param df: DataFrame to be visualized
    :param feature: name of the column with respect to which the plot will be coloured
    :param projection: name of projection to be visualized
    :param width: plot's width
    :param height: plot's height
    :return: plotly express scatter plot
    """
    projection_x = f"{projection.upper()}_X"
    projection_y = f"{projection.upper()}_Y"
    fig = px.scatter(
        df,
        x=projection_x,
        y=projection_y,
        text="CMPD ID",
        color=df[feature],
        range_color=[0, df[feature].max()],
        labels={
            projection_x: "X",
            projection_y: "Y",
            "CMPD ID": "Compound ID",
        },
        title=f"{projection.upper()} projection with respect to {feature}",
        width=width,
        height=height,
        hover_data={
            "CMPD ID": True,
            projection_x: ":.3f",
            projection_y: ":.3f",
            feature: ":.3f",
        },
    )

    fig.update_yaxes(title_standoff=15, automargin=True)
    fig.update_xaxes(title_standoff=30, automargin=True)
    fig.update_layout(
        modebar=dict(orientation="v"),
        margin=dict(r=35, l=15, b=0),
        title_x=0.5,
        coloraxis_colorbar=dict(orientation="h", thickness=15),
    )
    return fig


def visualize_multiple_plates(df: pd.DataFrame, plate_array: np.ndarray) -> plt.Figure:
    """
    Visualize plate values on grid 3x3

    :param df: DataFrame with plates
    :return: plot with visualized plates
    """
    fig, axes = plt.subplots(3, 3, constrained_layout=True)
    for ax, plate, barcode in zip(axes.flat, plate_array, df.barcode):
        im = ax.pcolormesh(plate[0])
        x, y = np.nonzero(plate[1])  # outliers
        ax.scatter(y + 0.5, x + 0.5, s=3, color="magenta")
        ax.set_title(barcode, fontsize=9)
        ax.axis("off")
    fig.colorbar(im, ax=axes.ravel().tolist(), location="bottom", aspect=60)
    return fig


def plot_control_values(df: pd.DataFrame) -> go.Figure:
    """
    Visualize mean positive and negative control values for each plate
    together with their standard devations

    :param df: DataFrame with control values
    :param plate_array: array with plate values
    :return: plotly figure
    """
    fig = go.Figure(
        layout_title_text="Control values for plates: mean and std",
        layout={
            "xaxis": {"title": "x-label", "visible": False, "showticklabels": False},
            "yaxis": {"title": "Value", "visible": True, "showticklabels": True},
            "margin": dict(
                l=10,
                r=10,
                t=50,
                b=10,
            ),
        },
    )
    fig.add_trace(
        go.Bar(
            name="CTRL NEG",
            x=df.barcode,
            y=df.mean_neg,
            error_y=dict(
                type="data", array=df.std_neg, color="gray", thickness=0.5, width=2
            ),
            marker_color="#d73027",
            marker_line_color="#d73027",
            opacity=0.75,
        )
    )
    fig.add_trace(
        go.Bar(
            name="CTRL POS",
            x=df.barcode,
            y=df.mean_pos,
            error_y=dict(
                type="data", array=df.std_pos, color="gray", thickness=0.5, width=2
            ),
            marker_color="#1a9850",
            marker_line_color="#1a9850",
            opacity=0.75,
        )
    )
    fig.update_layout(barmode="group")
    return fig


def plot_row_col_means(plate_array: np.ndarray) -> plt.Figure:
    """
    Plot mean values for each row and column across all plates

    :param plate_array: array with plate values
    :return: plt figure
    """
    arrays = plate_array[:, 0]
    outliers = plate_array[:, 1]
    arrays = np.where(outliers == 1, np.nan, arrays)
    params = [("column", 1), ("row", 2)]
    fig, axes = plt.subplots(1, 2, figsize=(14, 5))
    fig.suptitle("Mean values for columns and rows", fontsize=16)
    for i, p in enumerate(params):
        name, axis = p
        means = np.nanmean(arrays, axis=(0, axis))
        stds = np.nanstd(arrays, axis=(0, axis))
        ticks = range(1, means.shape[0] + 1)
        axes[i].bar(ticks, means, yerr=stds, alpha=0.75, ecolor="gray", capsize=5)
        axes[i].set_xlabel(name)
        axes[i].set_xticks(ticks)
        axes[i].set_xticklabels(axes[i].get_xticks(), rotation=90)
    return fig


def plot_z_per_plate(df: pd.DataFrame) -> plt.Figure:
    # TODO after outlier removal
    ...
