import pandas as pd
import plotly.express as px

from dash import dcc
from src.visualization.advanced_visualizations import plot_projection_2d


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
    projection_df: pd.DataFrame, colormap_feature: str, projection_type: str
) -> dcc.Graph:
    """
    Construct a scatterplot from a dataframe.

    :param projection_df: dataframe to construct plot from
    :param colormap_feature: feature to use for coloring
    :param projection_type: projection type
    :return: dcc Graph element containing the plot
    """
    return dcc.Graph(
        figure=plot_projection_2d(
            projection_df,
            colormap_feature,
            projection=projection_type,
            width=None,
            height=None,
        ),
        id="projection-plot",
    )
