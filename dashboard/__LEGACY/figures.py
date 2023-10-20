import pandas as pd
import plotly.express as px
from dash import dcc

from dashboard.visualization.overlay import projection_plot_overlay_controls
from dashboard.visualization.plots import plot_projection_2d


def make_scatterplot(
    df: pd.DataFrame, x: str, y: str, title: str, graph_id: str
) -> dcc.Graph:
    """
    Construct a scatterplot from a dataframe.

    :param df: dataframe to construct plot from
    :param x: x axis feature
    :param y: y axis feature
    :param title: plot title
    :param graph_id: id of the plot
    :return: dcc Graph element containing the plot
    """
    return dcc.Graph(
        figure=px.scatter(df, x=x, y=y, title=title),
        id=graph_id,
    )


def make_projection_plot(
    projection_df: pd.DataFrame,
    controls_df: pd.DataFrame,
    colormap_feature: str,
    projection_type: str,
    checkbox_values: list[str],
) -> dcc.Graph:
    """
    Construct a scatterplot from a dataframe.

    :param projection_df: dataframe to construct plot from
    :param colormap_feature: feature to use for coloring
    :param projection_type: projection type
    :param checkbox_values: list of checkbox values
    :return: dcc Graph element containing the plot
    """
    figure = plot_projection_2d(
        projection_df,
        colormap_feature,
        projection=projection_type,
        width=None,
        height=None,
    )
    if checkbox_values is not None and "add_controls" in checkbox_values:
        default_style = {
            "ALL NEGATIVE": ["#de425b", 12],
            "ALL POSITIVE": ["#488f31", 12],
            "ALL BUT ONE NEGATIVE": ["#eb7a52", 10],
            "ALL BUT ONE POSITIVE": ["#8aac49", 10],
        }
        if "cvd" in checkbox_values:
            default_style = {
                "ALL NEGATIVE": ["#a6611a", 12],
                "ALL POSITIVE": ["#018571", 12],
                "ALL BUT ONE NEGATIVE": ["#dfc27d", 10],
                "ALL BUT ONE POSITIVE": ["#80cdc1", 10],
            }

        figure = projection_plot_overlay_controls(
            figure,
            controls_df,
            default_style,
            projection=projection_type,
        )
    return dcc.Graph(
        figure=figure,
        id="projection-plot",
    )
