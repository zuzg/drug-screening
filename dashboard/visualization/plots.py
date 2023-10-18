from itertools import product

import numpy as np
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from dash import dash_table, html
from dash.dash_table.Format import Format, Scheme
from plotly.subplots import make_subplots

from dashboard.data.determination import four_param_logistic

PLOTLY_TEMPLATE = "plotly_white"


def table_from_df(df: pd.DataFrame, table_id: str) -> html.Div:
    """
    Construct a preview table from a dataframe.
    Includes all rows and columns.
    To limit the element size uses pagination.
    :param df: dataframe to construct table from
    :param table_id: id of the table
    :return: html Div element containing the table and heading
    """
    style_link = [
        {"id": x, "name": x, "type": "text", "presentation": "markdown"}
        if (x == "EOS")
        else {
            "id": x,
            "name": x,
            "type": "numeric",
            "format": Format(precision=3, scheme=Scheme.fixed),
        }
        for x in df.columns
    ]

    return html.Div(
        children=[
            dash_table.DataTable(
                columns=style_link,
                data=df.to_dict("records"),
                style_table={"overflowX": "auto", "overflowY": "auto"},
                style_data={
                    "padding-left": "10px",
                    "padding-right": "10px",
                    "width": "70px",
                    "autosize": {"type": "fit", "resize": True},
                    "overflow": "hidden",
                },
                style_cell={
                    "font-family": "sans-serif",
                    "font-size": "12px",
                },
                style_header={
                    "backgroundColor": "rgb(230, 230, 230)",
                    "fontWeight": "bold",
                },
                style_data_conditional=[
                    {
                        "if": {"row_index": "odd"},
                        "backgroundColor": "rgb(248, 248, 248)",
                    },
                ],
                filter_action="native",
                filter_options={"case": "insensitive"},
                sort_action="native",
                column_selectable=False,
                page_size=10,
                id=table_id,
            ),
        ],
        className="overflow-auto mx-2 border border-3 rounded shadow bg-body-tertiary",
    )


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
    feature_processed = feature.replace("_", " ").upper()
    fig = px.scatter(
        df,
        x=projection_x,
        y=projection_y,
        color=df[feature],
        range_color=[0, df[feature].max()],
        labels={
            projection_x: "X",
            projection_y: "Y",
            "EOS": "ID",
            feature: feature_processed,
        },
        title=f"{projection.upper()} projection with respect to {feature_processed}",
        # width=width,
        # height=height,
        hover_data={
            "EOS": True,
            projection_x: ":.3f",
            projection_y: ":.3f",
            feature: ":.3f",
        },
    )

    fig.update_traces(marker={"size": 8})
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

        fig.update_layout(
            {
                f"xaxis{i}": {"fixedrange": True, "showgrid": False},
                f"yaxis{i}": {
                    "fixedrange": True,
                    "showgrid": False,
                    "scaleanchor": f"x{i}",
                    "autorange": "reversed",
                },
                "autosize": True,
            }
        )

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
            "xaxis": {
                "title": "Barcode assay plate",
                "visible": True,
                "showticklabels": True,
                "tickfont": {"size": 1, "color": "rgba(0,0,0,0)"},
            },
            "yaxis": {
                "title": "Control value",
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
    fig.update_layout(
        template=PLOTLY_TEMPLATE,
        xaxis=dict(
            tickmode="linear",
            tick0=0.0,
            dtick=10,
        ),
    )
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
    params = [("Column", 1), ("Row", 2)]
    fig = make_subplots(
        rows=1,
        cols=2,
        shared_yaxes=True,
        horizontal_spacing=0.01,
    )
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
        fig.update_xaxes(title_text=f"{name} id", row=1, col=axis)
    fig.update_yaxes(title_text="Mean value for column/row")
    fig.update_layout(
        xaxis1=dict(
            tickmode="array",
            tickfont={"size": 8},
            tickvals=ticks_all[0][::2],
            ticktext=ticks_all[0][::2],
        ),
        xaxis2=dict(
            tickmode="array",
            tickfont={"size": 8},
            tickvals=ticks_all[1][::2],
            ticktext=ticks_all[1][::2],
        ),
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
                "tickfont": {"size": 1, "color": "rgba(0,0,0,0)"},
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
    fig.update_layout(
        template=PLOTLY_TEMPLATE,
        xaxis=dict(
            tickmode="linear",
            tick0=0.0,
            dtick=10,
        ),
    )
    return fig


def plot_activation_inhibition_zscore(
    compounds_df: pd.DataFrame,
    stats_dfs: list[pd.DataFrame],
    key: str,
    min_max_range: tuple[float],
) -> go.Figure:
    """
    Plot activation/inhibition z-score per plate.

    :compounds_df: dataframe with all compounds data
    :param stats_dfs: list of dataframes with stats
    :param key: key for stats df
    :param min_max_range: min and max range for plot
    :return: plotly figure
    """

    fig = go.Figure()
    colors = ["rgb(31, 119, 180)", "rgb(0,128,0)", "rgb(255,0,0)"]
    colors_shade = ["rgba(31, 119, 180,0.4)", "rgba(0,128,0,0.2)", "rgba(255,0,0,0.2)"]
    names = ["COMPOUNDS", "CONTROL POS", "CONTROL NEG"]

    PLATE = "Destination Plate Barcode"
    WELL = "Destination Well"

    cmpd_stats_df, pos_stats_df, neg_stats_df = stats_dfs
    pos_stats_df = pos_stats_df.merge(cmpd_stats_df[[f"{key}_x", PLATE]], on=PLATE)
    neg_stats_df = neg_stats_df.merge(cmpd_stats_df[[f"{key}_x", PLATE]], on=PLATE)
    stats_dfs = [cmpd_stats_df, pos_stats_df, neg_stats_df]

    for i, df in enumerate(stats_dfs):
        df = df.sort_values(by=[f"{key}_x"])

        fig.add_trace(
            go.Scatter(
                x=df[f"{key}_x"],
                y=df[f"{key}_mean"],
                line=dict(color=colors[i]),
                mode="lines+markers",
                name=names[i],
                legendgroup=names[i],
                customdata=np.stack(
                    (
                        df[PLATE],
                        df[f"{key}_std"],
                        df[f"{key}_min"],
                        df[f"{key}_max"],
                    ),
                    axis=-1,
                ),
                hovertemplate=f" {PLATE}<br>%{{customdata[0]}}<br>avg: %{{y:.4f}} &plusmn;%{{customdata[1]:.4f}}<br>min: %{{customdata[2]:.2f}}, max: %{{customdata[3]:.2f}}<extra></extra>",
            )
        )

        fig.add_trace(
            go.Scatter(
                x=pd.concat(
                    [df[f"{key}_x"], df[f"{key}_x"][::-1]], ignore_index=True
                ),  # x, then x reversed
                y=pd.concat(
                    [df[f"{key}_max"], df[f"{key}_min"][::-1]], ignore_index=True
                ),  # upper, then lower reversed
                fill="toself",
                fillcolor=colors_shade[i],
                line=dict(color="rgba(255,255,255,0)"),
                hoverinfo="skip",
                showlegend=False,
                name="Shaded Area",
                legendgroup=names[i],
            )
        )

        fig.update_layout(
            legend_itemsizing="constant",
            title=f"{key} of compounds and control values",
            xaxis=dict(
                {
                    "title": PLATE,
                    "visible": True,
                    "showticklabels": True,
                    "tickfont": {"size": 1, "color": "rgba(0,0,0,0)"},
                }
            ),
            yaxis_title=key,
            margin=dict(t=50, b=30, l=30, r=30),
            template=PLOTLY_TEMPLATE,
        )

    points = len(stats_dfs[0])
    min_coords = {
        "x": list(range(points)),
        "y": [min_max_range[0] for x in range(points)],
    }
    max_coords = {
        "x": list(range(points)),
        "y": [min_max_range[1] for x in range(points)],
    }

    fig.add_trace(
        go.Scatter(
            name="MIN/MAX range",
            x=min_coords["x"],
            y=min_coords["y"],
            mode="lines",
            legendgroup="MIN/MAX",
            hovertemplate=f"{key} min.: {min_coords['y'][0]}<extra></extra>",
            line=dict(color="red", dash="dash"),
        )
    )

    fig.add_trace(
        go.Scatter(
            name="max",
            x=max_coords["x"],
            y=max_coords["y"],
            mode="lines",
            legendgroup="MIN/MAX",
            showlegend=False,
            hovertemplate=f"{key} max.: {max_coords['y'][0]}<extra></extra>",
            line=dict(color="red", dash="dash"),
        )
    )

    mask = (compounds_df[key] >= min_max_range[0]) & (
        compounds_df[key] <= min_max_range[1]
    )
    outside_range_df = compounds_df[~mask].copy()
    outside_range_df = outside_range_df[[key, WELL, PLATE]].merge(
        cmpd_stats_df[[f"{key}_x", PLATE]], on=PLATE
    )

    fig.add_trace(
        go.Scatter(
            x=outside_range_df[f"{key}_x"],
            y=outside_range_df[key],
            mode="markers",
            marker=dict(color="blue", size=8),
            name="COMPOUNDS OUTSIDE",
            customdata=np.stack(
                (outside_range_df[PLATE], outside_range_df[WELL]), axis=-1
            ),
            text=compounds_df["EOS"],
            hovertemplate="plate: %{customdata[0]}<br>well: %{customdata[1]}<br>value: %{y:.4f}<extra>%{text}</extra>",
        )
    )

    return fig


def concentration_confirmatory_plot(
    act_inh_primary: np.ndarray,
    act_inh_secondary: np.ndarray,
    concentrations: np.ndarray,
    reaction_type: str,
) -> go.Figure:
    """
    Plot correlations of two screenings

    :param act_inh_primary: 1D array with act/inh values from primary screening
    :param act_inh_secondary: 1D array with act/inh values from secondary screening
    :param concentrations: 1D array with type of concentration
    :param reaction_type: inhibition or activation
    :return: plot figure
    """
    fig = px.scatter(
        x=act_inh_primary,
        y=act_inh_secondary,
        color=concentrations.astype(str),
        labels={
            "x": f"%{reaction_type} primary",
            "y": f"%{reaction_type} confirmatory",
            "color": "concentration",
        },
    )
    fig.update_layout(
        template=PLOTLY_TEMPLATE,
        title=f"{reaction_type} in primary and confirmatory screenings",
    )
    return fig


def concentration_plot(df: pd.DataFrame, reaction_type: str) -> go.Figure:
    """
    Plot activation/inhibition values for each compound by concentration

    :param df: Dataframe with inhibition/activation, id, and concentration
    :param reaction_type: inhibition or activation
    :return: plot figure
    """
    fig = go.Figure()
    # NOTE: to clarify
    value_by_conc = df.pivot_table(f"% {reaction_type}_x", "EOS", "Concentration")
    for _, row in value_by_conc.iterrows():
        fig.add_trace(
            go.Scatter(
                x=value_by_conc.columns,
                y=row.values,
                hovertemplate="EOS: %{text}<br>value: %{y}<extra></extra>",
                marker_symbol="square",
                marker_size=7,
                line_width=1,
                text=[str(row.name), str(row.name), str(row.name)],
            )
        )
    fig.update_layout(
        title_text="Concentrations",
        xaxis_title="Concentration [uM]",
        yaxis_title=reaction_type,
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


def plot_ic50(entry: dict, x: np.ndarray, y: np.ndarray) -> go.Figure:
    data = [
        go.Scatter(
            x=x,
            y=y,
            mode="markers",
            marker=dict(color="blue", size=6),
            name="Data points",
        )
    ]
    if not pd.isnull(entry["slope"]):
        # use logspace to get more points for fitting
        fit_x = np.logspace(np.log10(x.min()), np.log10(x.max()), 100)
        fit_y = four_param_logistic(
            fit_x,
            entry["lower_limit"],
            entry["upper_limit"],
            entry["ic50"],
            entry["slope"],
        )
        data.append(
            go.Scatter(
                x=fit_x,
                y=fit_y,
                mode="lines",
                marker=dict(color="red", size=10),
                name="Fitted curve",
            )
        )
        data.append(
            go.Scatter(
                x=[entry["ic50"]],
                y=[
                    four_param_logistic(
                        entry["ic50"],
                        entry["lower_limit"],
                        entry["upper_limit"],
                        entry["ic50"],
                        entry["slope"],
                    )
                ],
                mode="markers",
                marker=dict(color="red", size=10, symbol="diamond"),
                name="IC50",
            )
        )

    return go.Figure(
        layout_title_text="IC50",
        layout={
            "xaxis": {
                "title": "Concentration [uM]",
                "visible": True,
                "showticklabels": True,
                "type": "log",
            },
            "yaxis": {
                "title": "% Modulation",
                "visible": True,
                "showticklabels": True,
            },
        },
        data=data,
    )
