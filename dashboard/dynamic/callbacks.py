import typing

from dash import html, Dash
from dash.exceptions import PreventUpdate
from dash.dependencies import Input, Output, State

from .. import util
from .construct import construct_from_dataframes


def on_data_upload(
    contents: typing.Iterable,
    names: typing.Iterable[str],
) -> html.Div:
    if not contents:
        raise PreventUpdate
    dataframes = [util.parse_contents(c, n) for c, n in zip(contents, names)]
    updated_output = construct_from_dataframes(dataframes)
    return updated_output


def on_histogram_selection():
    ...


def register_callbacks(app: Dash) -> None:
    app.callback(
        Output("output-data-upload", "children"),
        Input("upload-data", "contents"),
        State("upload-data", "filename"),
    )(on_data_upload)
