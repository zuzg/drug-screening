"""
Construct functions create dynamic html elements from data.
"""

import pandas as pd
import plotly.express as px

from dash import html, dash_table, dcc


def construct_preview_table(df: pd.DataFrame, table_id: str) -> html.Div:
    """
    Construct a preview table from a dataframe.
    Includes all rows and columns.
    To limit the element size uses pagination.

    :param df: dataframe to construct table from
    :param table_id: id of the table
    :return: html Div element containing the table and heading
    """
    return html.Div(
        children=[
            html.H3("Data Preview", className="mb-2"),
            dash_table.DataTable(
                data=df.to_dict("records"),
                style_table={"overflow": "auto"},
                page_size=10,
                id=table_id,
            ),
        ],
        className="border rounded",
    )


def construct_description_table(df: pd.DataFrame, columns: list[str]) -> html.Div:
    """
    Construct a description table from a dataframe.
    Summarizes the stats for passed columns.

    :param df: dataframe to construct table from
    :param columns: list of the columns to summarize
    :return: html Div element containing the table and heading
    """
    return html.Div(
        children=[
            html.H3("Data Description", className="mb-2"),
            dash_table.DataTable(
                data=(
                    df.describe()[columns]
                    .round(3)
                    .T.reset_index(level=0)
                    .to_dict("records")
                ),
                style_table={"overflow": "auto"},
            ),
        ],
        className="border rounded",
    )


def construct_combined(
    combined_dataframe: pd.DataFrame, crucial_columns: list[str]
) -> html.Div:
    """
    Construct a vizualization from combined dataframe.

    :param combined_dataframe: merged dataframe of several experiments
    :param crucial_columns: list of column names to use for the vizualization
    :raises ValueError: if the dataframe does not have at least two crucial columns
    :return: html Div element containing the visualization
    """
    if len(crucial_columns) < 2:
        raise ValueError(
            "Combined dataframe must have at least two crucial columns columns."
        )
    description_table = construct_description_table(combined_dataframe, crucial_columns)
    scatter = dcc.Graph(
        figure=px.scatter(
            combined_dataframe,
            x=crucial_columns[0],
            y=crucial_columns[1],
            title="Scatterplot",
        ),
        id="value-scatterplot",
    )
    preview_table = construct_preview_table(
        combined_dataframe, "preview-table-combined"
    )
    return html.Div(children=[description_table, html.Hr(), scatter, preview_table])


def construct_single(dataframe: pd.DataFrame, crucial_columns: list[str]) -> html.Div:
    """
    Construct a vizualization from a single experiment.
    Currently only supports a histogram plot, description and preview tables.

    :param dataframe: dataframe of a singular experiment
    :param crucial_columns: list of column names to use for the vizualization
    :return: html Div element containing the visualization
    """
    crucial_column = crucial_columns[0]
    description_table = construct_description_table(dataframe, [crucial_column])
    histogram = dcc.Graph(
        figure=px.histogram(
            dataframe, x=crucial_column, title=f"{crucial_column} Histogram"
        ),
        id="value-histogram",
    )
    preview_table = construct_preview_table(dataframe, "preview-table")
    return html.Div(children=[description_table, html.Hr(), histogram, preview_table])
