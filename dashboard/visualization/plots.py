import string
from itertools import product

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots

PLOTLY_TEMPLATE = "plotly_white"


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
        template=PLOTLY_TEMPLATE,
    )
    return fig


def visualize_multiple_plates(
    df: pd.DataFrame, plate_array: np.ndarray, rows: int = 3, cols: int = 3
) -> go.Figure:
    """
    Visualize plate values on subplots 3x3

    :param df: DataFrame with plates
    :param plate_array: array with plate values
    :param rows: number of rows in plot grid
    :param cols: number of cols in plot grid
    :return: plot with visualized plates
    """
    fig = make_subplots(
        rows,
        cols,
        horizontal_spacing=0.01,
        vertical_spacing=0.05,
        subplot_titles=df.barcode.to_list(),
    )
    ids = product(list(range(1, rows + 1)), list(range(1, cols + 1)))
    for i, p, plate in zip(range(1, rows * cols + 1), ids, plate_array):
        fig.add_trace(
            go.Heatmap(
                z=plate[0],
                customdata=plate[1],
                coloraxis="coloraxis",
                hovertemplate="row: %{y}<br>column: %{x}<br>value: %{z}<br>outlier: %{customdata}<extra></extra>",
            ),
            p[0],
            p[1],
        )

        fig.update_layout({f"yaxis{i}": {"scaleanchor": f"x{i}"}, "autosize": True})

    fig.update_layout(
        coloraxis={"colorscale": "viridis"},
        plot_bgcolor="rgba(0,0,0,0)",
        margin=dict(
            l=10,
            r=10,
            t=20,
            b=10,
        ),
        template=PLOTLY_TEMPLATE,
    )
    fig.update_annotations(font_size=10)
    fig.update_xaxes(showticklabels=False)
    fig.update_yaxes(showticklabels=False)
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
        go.Scatter(
            name="CTRL NEG",
            x=df.barcode,
            y=df.mean_neg,
            error_y=dict(
                type="data", array=df.std_neg, color="gray", thickness=0.5, width=2
            ),
            mode="markers",
            marker_color="#d73027",
            marker_symbol="circle",
            opacity=0.75,
        )
    )
    fig.add_trace(
        go.Scatter(
            name="CTRL POS",
            x=df.barcode,
            y=df.mean_pos,
            error_y=dict(
                type="data", array=df.std_pos, color="gray", thickness=0.5, width=2
            ),
            mode="markers",
            marker_color="#1a9850",
            opacity=0.75,
        )
    )
    fig.update_layout(template=PLOTLY_TEMPLATE)
    return fig


def plot_row_col_means(plate_array: np.ndarray) -> go.Figure:
    """
    Plot mean values for each row and column across all plates

    :param plate_array: array with plate values
    :return: plotly figure
    """
    arrays = plate_array[:, 0]
    outliers = plate_array[:, 1]
    arrays = np.where(outliers == 1, np.nan, arrays)
    params = [("column", 1), ("row", 2)]
    fig = make_subplots(rows=1, cols=2)
    ticks_all = []
    for p in params:
        name, axis = p
        means = np.nanmean(arrays, axis=(0, axis))
        stds = np.nanstd(arrays, axis=(0, axis))
        ticks = [*range(1, means.shape[0] + 1)]
        ticks_all.append(ticks)
        fig.add_trace(
            go.Scatter(
                x=ticks,
                y=means,
                error_y=dict(
                    type="data", array=stds, color="gray", thickness=0.5, width=2
                ),
                mode="markers",
                marker_color="blue",
            ),
            row=1,
            col=axis,
        )
        fig.update_xaxes(title_text=f"{name}", row=1, col=axis)
    fig.update_layout(
        xaxis1=dict(tickmode="array", tickvals=ticks_all[0], ticktext=ticks_all[0]),
        xaxis2=dict(tickmode="array", tickvals=ticks_all[1], ticktext=ticks_all[1]),
    )
    fig.update_layout(
        title_text="Mean values for columns and rows",
        showlegend=False,
        margin=dict(
            l=10,
            r=10,
            t=50,
            b=10,
        ),
        template=PLOTLY_TEMPLATE,
    )
    return fig


def plot_z_per_plate(barcode: pd.Series, z_factor: pd.Series) -> go.Figure:
    """
    Visualize z factor per plate

    :param barcode: series containing plate barcodes
    :param z_factor: series containing plate z factors
    :return: plotly figure
    """
    fig = go.Figure(
        layout_title_text="Z' per plates",
        layout={
            "xaxis": {
                "title": "Barcode assay plate",
                "visible": True,
                "showticklabels": True,
            },
            "yaxis": {
                "title": "Z' after outliers removal",
                "visible": True,
                "showticklabels": True,
            },
            "margin": dict(
                l=10,
                r=10,
                t=50,
                b=10,
            ),
        },
    )
    fig.add_trace(
        go.Scatter(
            x=barcode,
            y=z_factor,
            mode="markers",
        )
    )
    fig.update_layout(template="plotly_white")
    return fig


def visualize_activation_inhibition_zscore(
    compounds_df: pd.DataFrame,
    control_pos_df: pd.DataFrame,
    control_neg_df: pd.DataFrame,
    column: str,
    z_score_limits: tuple = None,
) -> go.Figure:
    """
    Visualize activation/inhibition z-score for each compound
    :param compounds_df: dataframe with compounds
    :param control_pos_df: dataframe with positive controls
    :param control_neg_df: dataframe with negative controls
    :param column: column to visualize
    :param z_score_limits: tuple with z-score limits
    :return: plotly figure
    """
    dest_wells = pd.concat(
        [
            compounds_df["Destination Well"],
            control_pos_df["Destination Well"],
            control_neg_df["Destination Well"],
        ],
        axis=0,
        ignore_index=True,
    )
    dest_wells = pd.DataFrame(
        dest_wells, columns=["Destination Well"]
    ).drop_duplicates()

    sorted_wells = sorted(
        dest_wells["Destination Well"], key=lambda x: (x[0], int(x[1:]))
    )

    fig = go.Figure()

    fig.add_trace(
        go.Scatter(
            x=compounds_df["Destination Well"],
            y=compounds_df[column],
            hovertemplate="CMPD ID: TODO<br>Plate: %{text}<br>"
            + column
            + ": %{y:.4f}<extra></extra>",
            text=compounds_df["Destination Plate Barcode"],
            mode="markers",
            marker=dict(color="rgb(66, 167, 244)", size=8),
            name="COMPOUNDS",
        )
    )

    fig.add_trace(
        go.Scatter(
            x=control_pos_df["Destination Well"],
            y=control_pos_df[column],
            hovertemplate="CMPD ID: TODO<br>Plate: %{text}<br>"
            + column
            + ": %{y:.4f}<extra></extra>",
            text=control_pos_df["Destination Plate Barcode"],
            mode="markers",
            marker=dict(color="green", size=10),
            name="POSITIVE CONTROLS",
        )
    )

    fig.add_trace(
        go.Scatter(
            x=control_neg_df["Destination Well"],
            y=control_neg_df[column],
            hovertemplate="CMPD ID: TODO<br>Plate: %{text}<br>"
            + column
            + ": %{y:.4f}<extra></extra>",
            text=control_neg_df["Destination Plate Barcode"],
            mode="markers",
            marker=dict(color="red", size=10),
            name="NEGATIVE CONTROLS",
        )
    )

    fig.update_xaxes(type="category", categoryorder="array", categoryarray=sorted_wells)

    fig.update_layout(
        legend_itemsizing="constant",
        title=f"{column} values of compounds",
        xaxis_title="Well",
        yaxis_title=column,
        template=PLOTLY_TEMPLATE,
    )

    if column.upper() == "Z-SCORE" and z_score_limits is not None:
        fig.add_hline(
            y=z_score_limits[0],
            line_width=3,
            line_dash="dash",
            line_color="gray",
            annotation_text=f"MIN: {z_score_limits[0]:.2f}",
            annotation_font_color="gray",
        )
        fig.add_hline(
            y=z_score_limits[1],
            line_width=3,
            line_dash="dash",
            line_color="gray",
            annotation_text=f"MAX: {z_score_limits[1]:.2f}",
            annotation_font_color="gray",
        )

    return fig
