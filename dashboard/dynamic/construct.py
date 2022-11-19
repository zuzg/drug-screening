import typing

import pandas as pd
import plotly.express as px

from dash import html, dash_table, dcc
from src.data.parse_data import combine_experiments


def construct_combined(dataframes: typing.Iterable[pd.DataFrame]) -> html.Div:
    if len(dataframes) < 2:
        raise ValueError("Must have at least two dataframes to combine.")
    df = combine_experiments(dataframes)
    return html.Div(
        dash_table.DataTable(
            data=df.to_dict("records"),
            style_table={"overflowY": "auto"},
            page_size=10,
        ),
        className="border rounded",
    )


def construct_single(dataframe: pd.DataFrame) -> html.Div:
    value_columns = [
        col for col in ["% ACTIVATION", "VALUE"] if col in dataframe.columns
    ]
    if not value_columns:
        raise ValueError("No VALUE or % ACTIVATION columns found.")
    description_table = dash_table.DataTable(
        data=dataframe.describe()[value_columns].T.to_dict("records"),
        style_table={"overflowY": "auto"},
    )
    histogram = dcc.Graph(
        figure=px.histogram(dataframe, x=value_columns[0], title="Attribute Histogram"),
        id="attribute-histogram",
    )
    preview_table = dash_table.DataTable(
        id="preview-table",
        data=dataframe.to_dict("records"),
        style_table={"overflowY": "auto"},
        page_size=10,
    )
    return html.Div(children=[description_table, histogram, preview_table])


def construct_from_dataframes(dataframes: typing.Iterable[pd.DataFrame]) -> html.Div:
    return (
        construct_combined(dataframes) if len(dataframes) > 1 else construct_single(dataframes[0])
    )
