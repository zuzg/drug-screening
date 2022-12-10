"""
Defines and registers callbacks for the dashboard.
"""

import typing
import functools

from dash import html, Dash
from dash.exceptions import PreventUpdate
from dash.dependencies import Input, Output, State

from src.data.parse_data import combine_assays

from .tables import table_from_df
from .figures import scatterplot_from_df, make_projection_plot
from ..parse import parse_contents
from ..state import GlobalState


def on_data_upload(
    global_state: GlobalState,
    contents: typing.Iterable,
    names: typing.Iterable[str],
) -> tuple[html.Div, html.Div]:
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

    processed_dataframe = processed_dataframe[
        processed_dataframe["CMPD ID"].str.isnumeric() != False
    ]
    global_state.set_dataframe(processed_dataframe)

    description_table = table_from_df(
        global_state.strict_summary_df,
        "description-table",
    )
    preview_table = table_from_df(global_state.df, "preview-table")

    return (
        description_table,
        preview_table,
        global_state.crucial_columns,
        global_state.crucial_columns[0],
        global_state.crucial_columns,
        global_state.crucial_columns[0],
        global_state.crucial_columns,
        global_state.crucial_columns[0],
    )


def on_projection_plot_selection(
    global_state: GlobalState, relayoutData: dict, projection_type: str
) -> dict:
    """
    Callback on projection selection (i.e. zooming in).
    Limits the preview table records to the selected range.

    :param global_state: global state of the application containing the dataframe
    :param relayoutData: dictionary containing the new range
    :raises PreventUpdate: if no relayoutData passed
    :return: restricted dataframe as a dictionary
    """
    if not relayoutData or not projection_type:
        raise PreventUpdate

    df = global_state.projections_df
    if "xaxis.range[0]" in relayoutData:
        x_min = relayoutData["xaxis.range[0]"]
        x_max = relayoutData["xaxis.range[1]"]
        df = df[df[f"{projection_type}_X"].between(x_min, x_max)]
        y_min = relayoutData["yaxis.range[0]"]
        y_max = relayoutData["yaxis.range[1]"]
        df = df[df[f"{projection_type}_Y"].between(y_min, y_max)]
    return global_state.df[global_state.df["CMPD ID"].isin(df["CMPD ID"])].to_dict(
        "records"
    )


def on_axis_change(global_state: GlobalState, x_attr: str, y_attr: str) -> html.Div:
    """
    Callback on x axis dropdown change.
    Updates the basic plot.

    :param global_state: global state of the application containing the dataframe
    :param value: new x axis column name
    :return: html Div containing the basic plot
    """
    if not x_attr or not y_attr:
        raise PreventUpdate
    return scatterplot_from_df(
        global_state.strict_df,
        x_attr,
        y_attr,
        "Compounds experimens results",
        "basic-plot",
    )


def on_projection_settings_change(
    global_state: GlobalState, projection_type: str, colormap_attr: str
):
    if not projection_type or not colormap_attr:
        raise PreventUpdate
    return make_projection_plot(
        global_state.projections_df, colormap_attr, projection_type
    )


def register_callbacks(app: Dash, global_state: GlobalState) -> None:
    """
    Registers application callbacks.

    :param app: dash application
    :param global_state: global state of the application containing the dataframe
    """
    app.callback(
        [
            Output("description-table-slot", "children"),
            Output("preview-table-slot", "children"),
            Output("x-axis-dropdown", "options"),
            Output("x-axis-dropdown", "value"),
            Output("y-axis-dropdown", "options"),
            Output("y-axis-dropdown", "value"),
            Output("colormap-attribute-dropdown", "options"),
            Output("colormap-attribute-dropdown", "value"),
        ],
        Input("upload-data", "contents"),
        State("upload-data", "filename"),
    )(functools.partial(on_data_upload, global_state))
    app.callback(
        Output("preview-table", "data"),
        Input("projection-plot", "relayoutData"),
        State("projection-type-dropdown", "value"),
    )(functools.partial(on_projection_plot_selection, global_state))
    app.callback(
        Output("basic-plot-slot", "children"),
        [
            Input("x-axis-dropdown", "value"),
            Input("y-axis-dropdown", "value"),
        ],
    )(functools.partial(on_axis_change, global_state))
    app.callback(
        Output("projection-plot-slot", "children"),
        [
            Input("projection-type-dropdown", "value"),
            Input("colormap-attribute-dropdown", "value"),
        ],
    )(functools.partial(on_projection_settings_change, global_state))
