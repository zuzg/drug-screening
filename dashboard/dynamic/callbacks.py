"""
Defines and registers callbacks for the dashboard.
"""

import typing

import pandas as pd

from dash import html, Dash, dcc, callback_context
from dash.exceptions import PreventUpdate
from dash.dependencies import Input, Output, State
from sklearn.decomposition import PCA
from sklearn.manifold import TSNE
from umap import UMAP

from src.data.combine import combine_assays
from src.data.controls import generate_controls, controls_index_annotator
from src.data.utils import get_chemical_columns, generate_dummy_links_dataframe
from src.data.preprocess import MergedAssaysPreprocessor

from .tables import table_from_df, table_from_df_with_selected_columns
from .figures import make_scatterplot, make_projection_plot
from ..parse import parse_contents, get_crucial_column_names
from ..layout import PAGE_HOME, PAGE_ABOUT


def on_data_upload(
    contents: typing.Iterable,
    names: typing.Iterable[str],
) -> tuple[html.Div, html.Div, list[str], str, list[str], str, list[str], str]:
    """
    Callback on data upload.
    Parses the uploaded data.
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

    combined_df = combine_assays(zip(dataframes, names))
    chemical_columns = get_chemical_columns(combined_df.columns)

    # TODO: find better place to specify projectors
    base_projector_specs = [
        (PCA(n_components=2), "PCA"),
        (
            UMAP(
                n_components=2,
                n_neighbors=10,
                min_dist=0.1,
            ),
            "UMAP",
        ),
    ]
    combined_projector_specs = [
        (
            TSNE(n_components=2, learning_rate="auto", init="random", perplexity=3),
            "TSNE",
        ),
    ]

    # ==== MAIN DF PREPROCESSING ====

    ecbd_links = generate_dummy_links_dataframe(combined_df["CMPD ID"].to_list())
    main_preprocessor = (
        MergedAssaysPreprocessor(combined_df, chemical_columns)
        .restrict_to_chemicals()
        .drop_na()
        .append_ecbd_links(ecbd_links)
    )

    for projector, name in base_projector_specs:
        main_preprocessor.apply_projection(projector, name)
    processed_df = main_preprocessor.get_processed_df()

    # ==== END ====

    strict_summary_df = (
        processed_df[chemical_columns].describe().round(3).T.reset_index(level=0)
    )

    description_table = table_from_df(
        strict_summary_df,
        "description-table",
    )

    # ==== CONTROLS DF PREPROCESSING ====

    controls_df = generate_controls(chemical_columns)
    controls_preprocessor = MergedAssaysPreprocessor(controls_df, chemical_columns)
    for projector, name in base_projector_specs:
        controls_preprocessor.apply_projection(projector, name, just_transform=True)
    processed_controls_df = controls_preprocessor.get_processed_df()

    # ==== END ====

    # ==== TSNE PROJECTION + ANNOTATION ====
    # TODO: this part is a bit ugly, it'd be nice if we figure out a better solution for TSNE

    controls_with_main = pd.concat([processed_df, processed_controls_df]).reset_index()

    tsne_preprocessor = MergedAssaysPreprocessor(controls_with_main, chemical_columns)
    for projector, name in combined_projector_specs:
        tsne_preprocessor.apply_projection(projector, name).annotate_by_index(
            controls_index_annotator
        )
    merged_processed_df = tsne_preprocessor.get_processed_df()

    processed_df = merged_processed_df[
        merged_processed_df["annotation"] == "NOT CONTROL"
    ]
    processed_controls_df = merged_processed_df[
        merged_processed_df["annotation"] != "NOT CONTROL"
    ]

    # ==== END ====

    serialized_processed_df = processed_df.reset_index().to_json(
        date_format="iso", orient="split"
    )
    serialized_controls_df = processed_controls_df.reset_index().to_json(
        date_format="iso", orient="split"
    )

    return (
        serialized_processed_df,  # sent to data holder
        serialized_controls_df,  # sent to data holder
        description_table,
        [],  # trigger loader
    )


def on_home_button_click(
    click,
    serialized_projection_with_ecbd_links_df,
    table,
) -> tuple[html.Div, html.Div, list[str], str, list[str], str, list[str], str]:
    """
    Callback on home button click.
    Resets the dashboard to the initial state.

    :param click: click event
    :param serialized_projection_with_ecbd_links_df: jsonified projection dataframe
    :param table: table element
    :raises PreventUpdate: if no click event or no projection dataframe is provided
    :return: tuple of updated elements
    """

    if serialized_projection_with_ecbd_links_df is None:
        raise PreventUpdate

    projection_with_ecbd_links_df = pd.read_json(
        serialized_projection_with_ecbd_links_df, orient="split"
    )
    crucial_columns = get_crucial_column_names(projection_with_ecbd_links_df.columns)
    preview_table = table_from_df_with_selected_columns(
        projection_with_ecbd_links_df, "preview-table"
    )

    return (
        table,
        preview_table,
        crucial_columns,  # x-axis dropdown options
        crucial_columns[0],  # x-axis dropdown value
        crucial_columns,  # y-axis dropdown options
        crucial_columns[0],  # y-axis dropdown value
        crucial_columns,  # colormap-feature dropdown options
        crucial_columns[0],  # colormap-feature dropdown value
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
    if "yaxis.range[0]" in relayoutData:
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
    return make_scatterplot(
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


def on_page_change(*args):
    changed_id = [p["prop_id"] for p in callback_context.triggered][0]
    if "about-button" in changed_id:
        return PAGE_ABOUT
    return PAGE_HOME


def register_callbacks(app: Dash) -> None:
    """
    Registers application callbacks.

    :param app: dash application
    """
    app.callback(
        [
            Output("data-holder", "data"),
            Output("controls-holder", "data"),
            Output("table-holder", "data"),
            Output("dummy-loader", "children"),
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

    app.callback(
        Output("page-layout", "children"),
        Input("home-button", "n_clicks"),
        Input("about-button", "n_clicks"),
    )(on_page_change)

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
        [
            Input("home-button", "n_clicks"),
            Input("data-holder", "data"),
            Input("table-holder", "data"),
        ],
    )(on_home_button_click)
