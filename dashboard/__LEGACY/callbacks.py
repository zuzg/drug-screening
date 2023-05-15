"""
Defines and registers callbacks for the dashboard.
"""

import typing
import functools
import uuid

import pyarrow as pa
import pandas as pd

from dash import html, Dash, dcc, callback_context
from dash.exceptions import PreventUpdate
from dash.dependencies import Input, Output, State
from sklearn.decomposition import PCA
from sklearn.manifold import TSNE
from umap import UMAP

from dashboard.data.parse import parse_bytes_to_dataframe
from dashboard.data.combine import combine_assays
from dashboard.data.controls import generate_controls, controls_index_annotator
from dashboard.data.utils import get_chemical_columns, generate_dummy_links_dataframe
from dashboard.data.preprocess import MergedAssaysPreprocessor

from .tables import table_from_df, table_from_df_with_selected_columns
from .figures import make_scatterplot, make_projection_plot
from ..layout import PAGE_HOME, PAGE_ABOUT
from ..storage import FileStorage


def safe_load_data(
    file_storage: FileStorage, user_id: str, main: bool = True
) -> pd.DataFrame:
    file_type = "main" if main else "controls"
    file_name = f"{user_id}_{file_type}.pq"
    try:
        raw = file_storage.read_file(file_name)
    except FileNotFoundError:
        raise PreventUpdate
    return pd.read_parquet(pa.BufferReader(raw))


def on_data_upload(
    contents: typing.Iterable,
    names: typing.Iterable[str],
    stored_uuid: str,
    file_storage: FileStorage,
) -> tuple[html.Div, str, list]:
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
    if not stored_uuid:
        stored_uuid = str(uuid.uuid4())
    dataframes = [parse_bytes_to_dataframe(c, n) for c, n in zip(contents, names)]
    if len(dataframes) <= 1:
        raise ValueError("Only one file was uploaded.")

    names = [name.split(".")[0] for name in names]
    combined_df = combine_assays(dataframes, names)
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
    unique_ids = combined_df["CMPD ID"].unique().tolist()
    ecbd_links = generate_dummy_links_dataframe(unique_ids)
    main_preprocessor = (
        MergedAssaysPreprocessor(combined_df, chemical_columns)
        .restrict_to_chemicals()
        .drop_na()
        .group_duplicates_by_function("max")
        .dashboardend_ecbd_links(ecbd_links)
    )

    for projector, name in base_projector_specs:
        main_preprocessor.dashboardly_projection(projector, name)
    processed_df = main_preprocessor.get_processed_df()

    # ==== END ====

    # ==== CONTROLS DF PREPROCESSING ====
    controls_df = generate_controls(chemical_columns)
    controls_preprocessor = MergedAssaysPreprocessor(controls_df, chemical_columns)
    for projector, name in base_projector_specs:
        controls_preprocessor.dashboardly_projection(
            projector, name, just_transform=True
        )
    processed_controls_df = controls_preprocessor.get_processed_df()

    # ==== END ====

    # ==== TSNE PROJECTION + ANNOTATION ====
    # TODO: this part is a bit ugly, it'd be nice if we figure out a better solution for TSNE
    controls_with_main = pd.concat([processed_df, processed_controls_df]).reset_index()

    tsne_preprocessor = MergedAssaysPreprocessor(controls_with_main, chemical_columns)
    for projector, name in combined_projector_specs:
        tsne_preprocessor.dashboardly_projection(projector, name)
    merged_processed_df = tsne_preprocessor.annotate_by_index(
        controls_index_annotator
    ).get_processed_df()

    processed_df = merged_processed_df[
        merged_processed_df["annotation"] == "NOT CONTROL"
    ]
    processed_controls_df = merged_processed_df[
        merged_processed_df["annotation"] != "NOT CONTROL"
    ]

    # ==== END ====
    print("Serializing...")
    serialized_processed_df = processed_df.reset_index().to_parquet()
    serialized_controls_df = processed_controls_df.reset_index().to_parquet()

    file_storage.save_file(f"{stored_uuid}_main.pq", serialized_processed_df)
    file_storage.save_file(f"{stored_uuid}_controls.pq", serialized_controls_df)

    return (stored_uuid, [], 1)  # trigger loader


def on_home_button_click(
    click,
    dummy,
    user_uuid: str,
    file_storage: FileStorage,
) -> tuple[html.Div, html.Div, list[str], str, list[str], str, list[str], str]:
    """
    Callback on home button click.
    Resets the dashboard to the initial state.

    :param click: click event
    :param table: table element
    :raises PreventUpdate: if no click event or no projection dataframe is provided
    :return: tuple of updated elements
    """

    if not user_uuid:
        raise PreventUpdate

    projection_with_ecbd_links_df = safe_load_data(file_storage, user_uuid)
    crucial_columns = get_chemical_columns(projection_with_ecbd_links_df.columns)
    preview_table = table_from_df_with_selected_columns(
        projection_with_ecbd_links_df, "preview-table"
    )
    strict_summary_df = (
        projection_with_ecbd_links_df[crucial_columns]
        .describe()
        .round(3)
        .T.reset_index(level=0)
    )

    description_table = table_from_df(
        strict_summary_df,
        "description-table",
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
        [],
    )


def on_projection_plot_selection(
    relayoutData: dict, projection_type: str, user_uuid: str, file_storage: FileStorage
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
    if not relayoutData or not projection_type or not user_uuid:
        raise PreventUpdate

    df = safe_load_data(file_storage, user_uuid)
    if "xaxis.range[0]" in relayoutData:
        x_min = relayoutData["xaxis.range[0]"]
        x_max = relayoutData["xaxis.range[1]"]
        df = df[df[f"{projection_type}_X"].between(x_min, x_max)]
    if "yaxis.range[0]" in relayoutData:
        y_min = relayoutData["yaxis.range[0]"]
        y_max = relayoutData["yaxis.range[1]"]
        df = df[df[f"{projection_type}_Y"].between(y_min, y_max)]
    return df[df["CMPD ID"].isin(df["CMPD ID"])].round(3).to_dict("records")


def on_axis_change(
    x_attr: str, y_attr: str, user_uuid: str, file_storage: FileStorage
) -> dcc.Graph:
    """
    Callback on axis dropdown change.
    Updates the basic plot.

    :param x_attr: new x axis attribute
    :param y_attr: new y axis attribute
    :param projection_data: jsonified dataframe with projection data
    :return: html Div containing the basic plot
    """
    if not x_attr or not y_attr or not user_uuid:
        raise PreventUpdate
    df = safe_load_data(file_storage, user_uuid)
    return make_scatterplot(
        df,
        x_attr,
        y_attr,
        "Compounds experimens results",
        "basic-plot",
    )


def on_projection_settings_change(
    projection_type: str,
    colormap_attr: str,
    add_controls: bool,
    user_uuid: str,
    file_storage: FileStorage,
) -> dcc.Graph:
    """
    Callback on projection settings change.
    Updates the projection plot.

    :param projection_type: type of the projection to be visualized
    :param colormap_attr: column to be used for coloring the points
    :param add_controls: whether to add controls to the plot
    :raises PreventUpdate: if no projection_type or colormap_attr is provided
    :return: dcc Graph object representing the projection plot
    """
    if not projection_type or not colormap_attr or not user_uuid:
        raise PreventUpdate

    df = safe_load_data(file_storage, user_uuid)
    controls_df = safe_load_data(file_storage, user_uuid, main=False)

    return make_projection_plot(
        df,
        controls_df,
        colormap_attr,
        projection_type,
        add_controls,
    )


def on_page_change(*args):
    """
    Callback on page change.

    :return: new page
    """
    changed_id = [p["prop_id"] for p in callback_context.triggered][0]
    if "about-button" in changed_id:
        return PAGE_ABOUT
    return PAGE_HOME


def register_callbacks(dashboard: Dash, file_storage: FileStorage) -> None:
    """
    Registers dashboardlication callbacks.

    :param dashboard: dash dashboardlication
    """
    dashboard.callback(
        [
            Output("user-uuid", "data"),
            Output("dummy-loader", "children"),
            Output("home-button", "n_clicks"),
        ],
        Input("upload-data", "contents"),
        [State("upload-data", "filename"), State("user-uuid", "data")],
    )(functools.partial(on_data_upload, file_storage=file_storage))
    dashboard.callback(
        Output("preview-table", "data"),
        Input("projection-plot", "relayoutData"),
        [State("projection-type-dropdown", "value"), State("user-uuid", "data")],
    )(functools.partial(on_projection_plot_selection, file_storage=file_storage))
    dashboard.callback(
        Output("basic-plot-slot", "children"),
        [
            Input("x-axis-dropdown", "value"),
            Input("y-axis-dropdown", "value"),
        ],
        State("user-uuid", "data"),
    )(functools.partial(on_axis_change, file_storage=file_storage))
    dashboard.callback(
        Output("projection-plot-slot", "children"),
        [
            Input("projection-type-dropdown", "value"),
            Input("colormap-attribute-dropdown", "value"),
            Input("add-controls-checkbox", "value"),
        ],
        State("user-uuid", "data"),
    )(functools.partial(on_projection_settings_change, file_storage=file_storage))

    dashboard.callback(
        Output("page-layout", "children"),
        Input("home-button", "n_clicks"),
        Input("about-button", "n_clicks"),
    )(on_page_change)

    dashboard.callback(
        [
            Output("description-table-slot", "children"),
            Output("preview-table-slot", "children"),
            Output("x-axis-dropdown", "options"),
            Output("x-axis-dropdown", "value"),
            Output("y-axis-dropdown", "options"),
            Output("y-axis-dropdown", "value"),
            Output("colormap-attribute-dropdown", "options"),
            Output("colormap-attribute-dropdown", "value"),
            Output("dummy-loader-2", "children"),
        ],
        [
            Input("home-button", "n_clicks"),
            Input("dummy-loader-2", "children"),
        ],
        State("user-uuid", "data"),
    )(functools.partial(on_home_button_click, file_storage=file_storage))
