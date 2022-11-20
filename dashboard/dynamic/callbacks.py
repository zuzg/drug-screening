import typing
import functools

from dash import html, Dash
from dash.exceptions import PreventUpdate
from dash.dependencies import Input, Output, State

from src.data.parse_data import combine_experiments
from .construct import construct_single, construct_combined
from ..util import parse_contents
from ..state import GlobalState


def on_data_upload(
    global_state: GlobalState,
    contents: typing.Iterable,
    names: typing.Iterable[str],
) -> html.Div:
    if not contents:
        raise PreventUpdate

    dataframes = [parse_contents(c, n) for c, n in zip(contents, names)]
    processed_dataframe = dataframes[0]
    if len(dataframes) > 1:
        if dataframes[0].columns[0][:3] == "HRP":
            dataframes.reverse()
        processed_dataframe = combine_experiments(dataframes)
    global_state.df = processed_dataframe

    construct = construct_single if len(dataframes) == 1 else construct_combined
    data_visualization = construct(processed_dataframe)

    heading = html.H2(f"Data Preview for {', '.join(names)}", className="mb-5")
    return html.Div(children=[heading, data_visualization])


def on_histogram_selection(global_state: GlobalState, relayoutData: dict) -> dict:
    if not relayoutData:
        raise PreventUpdate
    df = global_state.df
    if "xaxis.range[0]" in relayoutData:
        x_min = relayoutData["xaxis.range[0]"]
        x_max = relayoutData["xaxis.range[1]"]
        df = df[df["VALUE"].between(x_min, x_max)]
    return df.to_dict("records")


def on_scatterplot_selection(global_state: GlobalState, relayoutData: dict) -> dict:
    if not relayoutData:
        raise PreventUpdate
    df = global_state.df
    columns = [col for col in df.columns if "VALUE" in col]
    if "xaxis.range[0]" in relayoutData:
        x_min = relayoutData["xaxis.range[0]"]
        x_max = relayoutData["xaxis.range[1]"]
        df = df[df[columns[0]].between(x_min, x_max)]
        y_min = relayoutData["yaxis.range[0]"]
        y_max = relayoutData["yaxis.range[1]"]
        df = df[df[columns[1]].between(y_min, y_max)]
    return df.to_dict("records")


def register_callbacks(app: Dash, global_state: GlobalState) -> None:
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
