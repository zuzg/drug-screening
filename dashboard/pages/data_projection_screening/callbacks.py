import base64
import functools
import io
import uuid
from datetime import datetime
from typing import List, Tuple

import pandas as pd
import plotly.graph_objects as go
import pyarrow as pa
from dash import Input, Output, State, callback, dcc, html, no_update
from sklearn.decomposition import PCA
from umap import UMAP

from dashboard.data.controls import controls_index_annotator, generate_controls
from dashboard.data.preprocess import MergedAssaysPreprocessor
from dashboard.data.utils import eos_to_ecbd_link
from dashboard.pages.components import make_file_list_component
from dashboard.storage import FileStorage
from dashboard.visualization.plots import make_projection_plot, plot_projection_2d
from dashboard.visualization.text_tables import pca_summary, table_from_df
from dashboard.pages.components import make_new_upload_view

PROJECTION_SETUP = [
    (PCA(n_components=3), "PCA"),
    (
        UMAP(
            n_components=2,
            n_neighbors=10,
            min_dist=0.1,
        ),
        "UMAP",
    ),
    (
        UMAP(
            n_components=3,
            n_neighbors=10,
            min_dist=0.1,
        ),
        "UMAP3D",
    ),
]

# === STAGE 1 ===


def on_projection_files_upload(
    content: str | None,
    filenames: List[str],
    last_modified: int,
    stored_uuid: str,
    file_storage: FileStorage,
) -> tuple[html.Div, str, html.Div, bool]:
    """
    Callback for file upload.

    :param content: base64 encoded file content
    :param stored_uuid: session uuid
    :param file_storage: file storage
    :return: icon indicating the status of the upload
    :return: uuid of the stored data
    """
    if content is None:
        return no_update
    if stored_uuid is None:
        stored_uuid = str(uuid.uuid4())
    if len(filenames) < 3:
        return (
            html.Div(
                children=[
                    html.I(className="fas fa-exclamation-circle me-2"),
                    html.Span("You need to upload at least 3 files."),
                ],
                className="alert alert-danger",
            ),
            make_new_upload_view(
                "You need to upload at least 3 files.", "new Screening files (.csv)"
            ),
            stored_uuid,
            no_update,
            True,
        )

    projection_files = []

    for content, filename in zip(content, filenames):
        filename, extension = filename.split(".")
        if extension == "csv":
            decoded = base64.b64decode(content.split(",")[1]).decode("utf-8")
            projection_files.append((filename, io.StringIO(decoded)))

    if projection_files:
        assays_preprocessor = MergedAssaysPreprocessor()
        assays_preprocessor.combine_assays_for_projections(tuple(projection_files))
        assays_merged_df = assays_preprocessor.get_processed_compounds_df()

    saved_name = f"{stored_uuid}_assays_merged.pq"
    file_storage.save_file(saved_name, assays_merged_df.reset_index().to_parquet())

    return (
        html.Div(
            children=[
                make_file_list_component(filenames, [], 1),
            ],
        ),
        make_new_upload_view(
            "Files uploaded successfully", "new Screening files (.csv)"
        ),
        stored_uuid,
        no_update,
        False,
    )


# === STAGE 2 ===


def on_projections_visualization_entry(
    current_stage: int,
    stored_uuid: str,
    file_storage: FileStorage,
) -> Tuple[go.Figure, html.Div, html.Div, html.Div, html.Div, html.Div]:
    """
    Callback for projections visualization stage entry.
    It loads the data from the storage, computes and visualizes the projections.

    :param current_stage: index of the current stage
    :param stored_uuid: session uuid
    :param file_storage: file storage
    :return: figure with projections, table with projections, dropdown with projection attributes,
    dropdown with projection methods, projection info, checkbox for controls
    """
    if current_stage != 1:
        return no_update

    load_name = f"{stored_uuid}_assays_merged.pq"
    merged_df = pd.read_parquet(pa.BufferReader(file_storage.read_file(load_name)))

    # take only columns with projections i.e. having % in the name
    projection_columns = [col for col in merged_df.columns if "%" in col]
    controls_df = generate_controls(projection_columns)

    assays_preprocessor = MergedAssaysPreprocessor()
    assays_preprocessor.set_compounds_df(merged_df).set_controls_df(
        controls_df
    ).set_columns_for_projection(projection_columns)

    for projector, name in PROJECTION_SETUP:
        assays_preprocessor.apply_projection(projector, name)

    projections_df = assays_preprocessor.get_processed_compounds_df()
    file_storage.save_file(
        f"{stored_uuid}_assays_projection.pq",
        projections_df.reset_index(drop=True).to_parquet(),
    )

    projection_controls_df = assays_preprocessor.annotate_controls(
        controls_index_annotator
    ).get_processed_controls_df()
    file_storage.save_file(
        f"{stored_uuid}_controls_projection.pq",
        projection_controls_df.reset_index(drop=True).to_parquet(),
    )

    dropdown_options = []
    for value in projection_columns:
        option = {"label": value, "value": value}
        dropdown_options.append(option)

    fig = plot_projection_2d(projections_df, projection_columns[0], "PCA")
    projections_df = eos_to_ecbd_link(projections_df)
    table = table_from_df(projections_df, "projection-table")

    attribute_options = html.Div(
        children=[
            dcc.Dropdown(
                id="projection-attribute-selection-box",
                options=dropdown_options,
                value=projection_columns[0],
                searchable=False,
                clearable=False,
                disabled=False,
            ),
        ]
    )

    pca = PROJECTION_SETUP[0][0]
    projection_info = pca_summary(pca, projection_columns)

    return fig, table, attribute_options, projection_info, False


def on_checkbox_change(
    projection_type: str,
    attribute: str,
    controls: List[str],
    plot_3d: List[str],
    stored_uuid: str,
    file_storage: FileStorage,
) -> go.Figure:
    """
    Callback for dropdown change. It loads the data from the storage and visualizes the projections.

    :param method: projection method
    :param attribute: projection attribute
    :param controls: controls checkbox
    :param plot_3d: 3d checkbox
    :param stored_uuid: session uuid
    :param file_storage: file storage
    :return: figure with projections
    """
    compounds_df = pd.read_parquet(
        pa.BufferReader(file_storage.read_file(f"{stored_uuid}_assays_projection.pq"))
    )
    controls_df = pd.read_parquet(
        pa.BufferReader(file_storage.read_file(f"{stored_uuid}_controls_projection.pq"))
    )

    return make_projection_plot(
        compounds_df,
        controls_df,
        attribute,
        projection_type,
        bool(controls),
        bool(plot_3d),
    )


def on_plot_zommed_in(
    relayout_data: dict,
    stored_uuid: str,
    projection_type: str,
    file_storage: FileStorage,
) -> None:
    if not relayout_data:
        return no_update

    try:
        df = pd.read_parquet(
            pa.BufferReader(
                file_storage.read_file(f"{stored_uuid}_assays_projection.pq")
            ),
        )
    except FileNotFoundError:
        return no_update

    if "xaxis.range[0]" in relayout_data:
        x_min = relayout_data["xaxis.range[0]"]
        x_max = relayout_data["xaxis.range[1]"]
        df = df[df[f"{projection_type}_X"].between(x_min, x_max)]
    if "yaxis.range[0]" in relayout_data:
        y_min = relayout_data["yaxis.range[0]"]
        y_max = relayout_data["yaxis.range[1]"]
        df = df[df[f"{projection_type}_Y"].between(y_min, y_max)]

    return eos_to_ecbd_link(df).to_dict("records")


def on_projection_download_selection_button_click(
    n_clicks: int,
    selection: dict,
    stored_uuid: str,
    file_storage: FileStorage,
) -> dict:
    """
    Callback for the download selected button click. Downloads lasso/box selected datapoints
    to a csv file.

    :param n_clicks: number of clicks
    :param stored_uuid: session uuid
    :param file_storage: storage object
    """
    if not selection:
        return no_update

    datapoints = [point["pointIndex"] for point in selection["points"]]

    df = pd.read_parquet(
        pa.BufferReader(file_storage.read_file(f"{stored_uuid}_assays_projection.pq")),
    )
    selected_subset_df = df.iloc[datapoints]
    filename = f"projection_data_{datetime.now().strftime('%Y-%m-%d')}-selection-{selected_subset_df.shape[0]}.csv"
    return dcc.send_data_frame(selected_subset_df.to_csv, filename)


def on_3d_checkbox_change(plot_3d: List[str]) -> bool:
    """
    Callback for the 3d checkbox change. Disables the download selection button if 3d is selected.


    :param plot_3d: 3d checkbox selection
    :return: boolean indicating if the button should be disabled
    """
    return bool(plot_3d)


# === STAGE 3 ===


def on_save_results_entry(current_stage: int):
    if current_stage != 2:
        return no_update
    return False


def on_save_projections_click(
    n_clicks: int,
    stored_uuid: str,
    file_storage: FileStorage,
) -> dict:
    """
    Callback for the save projections button

    :param n_clicks: number of clicks
    :param stored_uuid: uuid of the stored data
    :param file_storage: storage object
    :return: None
    """

    filename = f"projection_data_{datetime.now().strftime('%Y-%m-%d')}.csv"

    projections_df = pd.read_parquet(
        pa.BufferReader(file_storage.read_file(f"{stored_uuid}_assays_projection.pq")),
    )

    return dcc.send_data_frame(projections_df.to_csv, filename)


def register_callbacks(elements, file_storage: FileStorage):
    callback(
        Output("projections-file-message", "children"),
        Output("upload-projection-data", "children"),
        Output("user-uuid", "data", allow_duplicate=True),
        Output("dummy-upload-projection-data", "children"),
        Output({"type": elements["BLOCKER"], "index": 0}, "data"),
        Input("upload-projection-data", "contents"),
        Input("upload-projection-data", "filename"),
        Input("upload-projection-data", "last_modified"),
        State("user-uuid", "data"),
        prevent_initial_call=True,
    )(functools.partial(on_projection_files_upload, file_storage=file_storage))
    callback(
        Output("projection-plot", "figure", allow_duplicate=True),
        Output("projection-table", "children"),
        Output("projection-attribute-selection-box", "children"),
        Output("pca-info", "children"),
        Output({"type": elements["BLOCKER"], "index": 1}, "data"),
        Input(elements["STAGES_STORE"], "data"),
        State("user-uuid", "data"),
        prevent_initial_call=True,
    )(functools.partial(on_projections_visualization_entry, file_storage=file_storage))
    callback(
        Output("projection-plot", "figure", allow_duplicate=True),
        Input("projection-method-selection-box", "value"),
        Input("projection-attribute-selection-box", "value"),
        Input("control-checkbox", "value"),
        Input("3d-checkbox", "value"),
        State("user-uuid", "data"),
        prevent_initial_call=True,
    )(functools.partial(on_checkbox_change, file_storage=file_storage))
    callback(
        Output("projection-download-selection-csv", "data"),
        Input("projection-download-selection-button", "n_clicks"),
        State("projection-plot", "selectedData"),
        State("user-uuid", "data"),
        prevent_initial_call=True,
    )(
        functools.partial(
            on_projection_download_selection_button_click, file_storage=file_storage
        )
    )
    callback(
        Output("projection-download-selection-button", "disabled"),
        Input("3d-checkbox", "value"),
    )(on_3d_checkbox_change)
    callback(
        Output({"type": elements["BLOCKER"], "index": 2}, "data"),
        Input(elements["STAGES_STORE"], "data"),
    )(on_save_results_entry)
    callback(
        Output("download-projections-csv", "data"),
        Input("save-projections-button", "n_clicks"),
        State("user-uuid", "data"),
        prevent_initial_call=True,
    )(functools.partial(on_save_projections_click, file_storage=file_storage))
    callback(
        Output("projection-table", "data"),
        Input("projection-plot", "relayoutData"),
        State("user-uuid", "data"),
        State("projection-method-selection-box", "value"),
        prevent_initial_call=True,
    )(functools.partial(on_plot_zommed_in, file_storage=file_storage))
