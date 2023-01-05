import pandas as pd
import plotly.express as px

from dash import dcc
from src.visualization.advanced_visualizations import plot_projection_2d, projection_2d_add_controls
from src.data.parse_data import split_controls_pos_neg

def scatterplot_from_df(
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
    projection_df: pd.DataFrame, controls_df: pd.DataFrame, colormap_feature: str, projection_type: str, checkbox_values: bool
) -> dcc.Graph:
    """
    Construct a scatterplot from a dataframe.

    :param projection_df: dataframe to construct plot from
    :param colormap_feature: feature to use for coloring
    :param projection_type: projection type
    :param add_controls: add control values option
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
        control_points = split_controls_pos_neg(controls_df, colormap_feature)
        if "cvd" in checkbox_values:
            return dcc.Graph(
            figure=projection_2d_add_controls(figure, control_points, projection=projection_type, cvd=True),
            id="projection-plot",
            )
        return dcc.Graph(
            figure=projection_2d_add_controls(figure, control_points, projection=projection_type),
            id="projection-plot",
        )
  
    return dcc.Graph(
        figure=figure,
        id="projection-plot",
    )
