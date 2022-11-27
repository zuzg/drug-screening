"""
Defines and registers callbacks for the dashboard.
"""

import typing
import functools

from dash import html, Dash
from dash.exceptions import PreventUpdate
from dash.dependencies import Input, Output, State

from src.data.parse_data import combine_assays
from .construct import construct_single, construct_combined
from ..util import parse_contents
from ..state import GlobalState


def on_data_upload(
    global_state: GlobalState,
    contents: typing.Iterable,
    names: typing.Iterable[str],
) -> html.Div:
    """
    Callback on files being uploaded.
    Merges received dataframes and updates the global state.

    :param global_state: global state of the application containing the dataframe
    :param contents: collection of file contents
    :param names: collection of file names
    :raises PreventUpdate: if no files were uploaded
    :return: html Div containing the heading and entire data vizualization
    """
    if not contents:
        raise PreventUpdate

    dataframes = [parse_contents(c, n) for c, n in zip(contents, names)]
    processed_dataframe = dataframes[0]
    if len(dataframes) > 1:
        processed_dataframe = combine_assays(zip(dataframes, names))

    global_state.set_dataframe(processed_dataframe)

    construct = construct_single if len(dataframes) == 1 else construct_combined
    data_visualization = construct(global_state.df, global_state.crucial_columns)

    heading = html.H2(f"Data Preview for {', '.join(names)}", className="mb-5")
    return html.Div(children=[heading, data_visualization])


def on_histogram_selection(global_state: GlobalState, relayoutData: dict) -> dict:
    """
    Callback on histogram selection (i.e. zooming in).
    Limits the preview table records to the selected range.

    :param global_state: global state of the application containing the dataframe
    :param relayoutData: dictionary containing the new range
    :raises PreventUpdate: if no relayoutData passed
    :return: restricted dataframe as a dictionary
    """
    if not relayoutData:
        raise PreventUpdate
    df = global_state.df

    # if range not specified include all entries from original dataframe
    if "xaxis.range[0]" in relayoutData:
        x_min = relayoutData["xaxis.range[0]"]
        x_max = relayoutData["xaxis.range[1]"]
        df = df[df[global_state.crucial_columns[0]].between(x_min, x_max)]
    return df.to_dict("records")


def on_scatterplot_selection(global_state: GlobalState, relayoutData: dict) -> dict:
    """
    Callback on scatterplot selection (i.e. zooming in).
    Limits the preview table records to the selected range.
    Assumes that the scatterplot is a 2D plot and that the x-axis is the first VALUE column.
    (the y-axis is the second VALUE column).

    :param global_state: global state of the application containing the dataframe
    :param relayoutData: dictionary containing the new range
    :raises PreventUpdate: if no relayoutData passed
    :return: restricted dataframe as a dictionary
    """
    if not relayoutData:
        raise PreventUpdate

    df = global_state.df

    # if range specified restrict entries to ones having values in range
    if "xaxis.range[0]" in relayoutData:
        x_min = relayoutData["xaxis.range[0]"]
        x_max = relayoutData["xaxis.range[1]"]
        df = df[df[global_state.crucial_columns[0]].between(x_min, x_max)]
        y_min = relayoutData["yaxis.range[0]"]
        y_max = relayoutData["yaxis.range[1]"]
        df = df[df[global_state.crucial_columns[1]].between(y_min, y_max)]
    return df.to_dict("records")


def register_callbacks(app: Dash, global_state: GlobalState) -> None:
    """
    Registers application callbacks.

    :param app: dash application
    :param global_state: global state of the application containing the dataframe
    """
    app.callback(
        Output("output-data-upload", "children"),
        Input("upload-data", "contents"),
        State("upload-data", "filename"),
    )(functools.partial(on_data_upload, global_state))
    app.callback(
        Output("preview-table", "data"),
        Input("value-histogram", "relayoutData"),
    )(functools.partial(on_histogram_selection, global_state))
    app.callback(
        Output("preview-table-combined", "data"),
        Input("value-scatterplot", "relayoutData"),
    )(functools.partial(on_scatterplot_selection, global_state))
