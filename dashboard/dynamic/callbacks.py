"""
Defines and registers callbacks for the dashboard.
"""

import typing

import pandas as pd

from dash import html, Dash, dcc
from dash.exceptions import PreventUpdate
from dash.dependencies import Input, Output, State

from src.data.parse_data import combine_assays, get_projections, add_ecbd_links, get_control_rows

from .tables import table_from_df, table_from_df_with_selected_columns
from .figures import scatterplot_from_df, make_projection_plot
from ..parse import parse_contents, get_crucial_column_names


def on_data_upload(
    contents: typing.Iterable,
    names: typing.Iterable[str],
) -> tuple[html.Div, html.Div, list[str], str, list[str], str, list[str], str]:
    """
    Callback on data upload.
    Parses the uploaded data and updates the description table, preview table, and dropdowns.
    Creates projection dataframe and passes it to client-side data-holder.
    Only accepts two or more files.

    :param contents: list of uploaded file contents
    :param names: list of uploaded file names
    :raises PreventUpdate: if no files were uploaded
    :raises ValueError: if only one file was uploaded
    :return: tuple of updated elements
    """
    if not contents:
        raise PreventUpdate

    dataframes = [parse_contents(c, n) for c, n in zip(contents, names)]
    if len(dataframes) <= 1:
        raise ValueError("Only one file was uploaded.")

    processed_dataframe = combine_assays(zip(dataframes, names))

    # Workaround for the bug in the parse_data module
    try:
        processed_dataframe = processed_dataframe[
            processed_dataframe["CMPD ID"].str.isnumeric() != False
        ]
    except AttributeError:
        pass

    crucial_columns = get_crucial_column_names(processed_dataframe.columns)

    strict_df = processed_dataframe[["CMPD ID"] + crucial_columns]
    strict_summary_df = (
        strict_df[crucial_columns].describe().round(3).T.reset_index(level=0)
    )
    description_table = table_from_df(
        strict_summary_df,
        "description-table",
    )
    controls = get_control_rows(strict_df)
    projection_df, controls_df = get_projections(strict_df, controls)
    projection_with_ecbd_links_df = add_ecbd_links(projection_df)
    serialized_projection_with_ecbd_links_df = projection_with_ecbd_links_df.to_json(
        date_format="iso", orient="split"
    )

    serialized_controls_df = controls_df.to_json(date_format="iso", orient="split")
    preview_table = table_from_df_with_selected_columns(
        projection_with_ecbd_links_df, "preview-table"
    )

    return (
        description_table,
        preview_table,
        crucial_columns,  # x-axis dropdown options
        crucial_columns[0],  # x-axis dropdown value
        crucial_columns,  # y-axis dropdown options
        crucial_columns[0],  # y-axis dropdown value
        crucial_columns,  # colormap-feature dropdown options
        crucial_columns[0],  # colormap-feature dropdown value
        serialized_projection_with_ecbd_links_df,  # sent to data holder
        serialized_controls_df,  # sent to data holder
    )


def on_projection_plot_selection(
    relayoutData: dict, projection_type: str, projection_data: str
) -> dict:
    """
    Callback on projection selection (i.e. zooming in).
    Limits the preview table records to the selected range.

    :param relayoutData: dictionary containing the new range
    :param projection_type: type of the projection
    :param projection_data: jsonified dataframe with projection data
    :raises PreventUpdate: if no relayoutData or projection_type is provided
    :return: restricted dataframe as a dictionary
    """
    if not relayoutData or not projection_type:
        raise PreventUpdate

    df = pd.read_json(projection_data, orient="split")
    if "xaxis.range[0]" in relayoutData:
        x_min = relayoutData["xaxis.range[0]"]
        x_max = relayoutData["xaxis.range[1]"]
        df = df[df[f"{projection_type}_X"].between(x_min, x_max)]
        y_min = relayoutData["yaxis.range[0]"]
        y_max = relayoutData["yaxis.range[1]"]
        df = df[df[f"{projection_type}_Y"].between(y_min, y_max)]
    return df[df["CMPD ID"].isin(df["CMPD ID"])].round(3).to_dict("records")


def on_axis_change(x_attr: str, y_attr: str, projection_data: str) -> dcc.Graph:
    """
    Callback on axis dropdown change.
    Updates the basic plot.

    :param x_attr: new x axis attribute
    :param y_attr: new y axis attribute
    :param projection_data: jsonified dataframe with projection data
    :return: html Div containing the basic plot
    """
    if not x_attr or not y_attr:
        raise PreventUpdate
    return scatterplot_from_df(
        pd.read_json(projection_data, orient="split"),
        x_attr,
        y_attr,
        "Compounds experimens results",
        "basic-plot",
    )


def on_projection_settings_change(
    projection_type: str,
    colormap_attr: str,
    add_controls: bool,
    projection_data: str,
    controls_data: str,
) -> dcc.Graph:
    """
    Callback on projection settings change.
    Updates the projection plot.

    :param projection_type: type of the projection to be visualized
    :param colormap_attr: column to be used for coloring the points
    :param global_state: global state of the application contaiing the dataframe
    :raises PreventUpdate: if no projection_type or colormap_attr is provided
    :return: dcc Graph object representing the projection plot
    """
    if not projection_type or not colormap_attr:
        raise PreventUpdate
    return make_projection_plot(
        pd.read_json(projection_data, orient="split"),
        pd.read_json(controls_data, orient="split"),
        colormap_attr,
        projection_type,
        add_controls,
    )


def register_callbacks(app: Dash) -> None:
    """
    Registers application callbacks.

    :param app: dash application
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
            Output("data-holder", "data"),
            Output("controls-holder", "data"),
        ],
        Input("upload-data", "contents"),
        State("upload-data", "filename"),
    )(on_data_upload)
    app.callback(
        Output("preview-table", "data"),
        Input("projection-plot", "relayoutData"),
        [
            State("projection-type-dropdown", "value"),
            State("data-holder", "data"),
        ],
    )(on_projection_plot_selection)
    app.callback(
        Output("basic-plot-slot", "children"),
        [
            Input("x-axis-dropdown", "value"),
            Input("y-axis-dropdown", "value"),
        ],
        State("data-holder", "data"),
    )(on_axis_change)
    app.callback(
        Output("projection-plot-slot", "children"),
        [
            Input("projection-type-dropdown", "value"),
            Input("colormap-attribute-dropdown", "value"),
            Input("add-controls-checkbox", "value"),
        ],
        State("data-holder", "data"),
        State("controls-holder", "data"),
    )(on_projection_settings_change)
