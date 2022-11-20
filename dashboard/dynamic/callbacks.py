import typing
import functools

import pandas as pd

from dash import html, Dash
from dash.exceptions import PreventUpdate
from dash.dependencies import Input, Output, State

from ..util import parse_contents
from .construct import construct_from_dataframes


def on_data_upload(
    global_state: list[pd.DataFrame],
    contents: typing.Iterable,
    names: typing.Iterable[str],
) -> html.Div:
    if not contents:
        raise PreventUpdate
    dataframes = [parse_contents(c, n) for c, n in zip(contents, names)]
    global_state[:] = dataframes
    heading = html.H2(f"Data Preview for {', '.join(names)}", className="mb-5")
    data_visualization = construct_from_dataframes(dataframes)
    return html.Div(children=[heading, data_visualization])


def on_histogram_selection(
    global_state: list[pd.DataFrame], relayoutData: dict
) -> dict:
    if not relayoutData:
        raise PreventUpdate
    df = global_state[0]
    if "xaxis.range[0]" in relayoutData:
        x_min = relayoutData["xaxis.range[0]"]
        x_max = relayoutData["xaxis.range[1]"]
        df = df[df["VALUE"].between(x_min, x_max)]
    return df.to_dict("records")


def register_callbacks(app: Dash, global_state: list[pd.DataFrame]) -> None:
    app.callback(
        Output("output-data-upload", "children"),
        Input("upload-data", "contents"),
        State("upload-data", "filename"),
    )(functools.partial(on_data_upload, global_state))
    app.callback(
        Output("preview-table", "data"),
        Input("attribute-histogram", "relayoutData"),
    )(functools.partial(on_histogram_selection, global_state))
