import base64
import functools
import io
import uuid
from datetime import datetime

import pandas as pd
import plotly.graph_objects as go
import pyarrow as pa
from dash import Input, Output, State, callback, dcc, html, no_update
from sklearn.decomposition import PCA
from umap import UMAP

from dashboard.data.preprocess import MergedAssaysPreprocessor
from dashboard.data.utils import eos_to_ecbd_link
from dashboard.pages.components import make_file_list_component
from dashboard.storage import FileStorage
from dashboard.visualization.plots import plot_projection_2d, table_from_df

PROJECTION_SETUP = [
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

# === STAGE 1 ===


def on_projection_files_upload(
    content: str | None,
    filenames: list[str],
    last_modified: int,
    stored_uuid: str,
    file_storage: FileStorage,
) -> html.Div:
    """
    Callback for file upload. TBD

    :param content: base64 encoded file content
    :param stored_uuid: session uuid
    :param file_storage: file storage
    :return: icon indicating the status of the upload
    """
    if content is None:
        return no_update
    if stored_uuid is None:
        stored_uuid = str(uuid.uuid4())

    projection_files = []

    for content, filename in zip(content, filenames):
        filename, extension = filename.split(".")
        if extension == "csv":
            decoded = base64.b64decode(content.split(",")[1]).decode("utf-8")
            projection_files.append((filename, io.StringIO(decoded)))

    if projection_files:
        assays_preprocessor = MergedAssaysPreprocessor()
        assays_preprocessor.combine_assays_for_projections(tuple(projection_files))
        assays_merged_df = assays_preprocessor.get_processed_df()

    saved_name = f"{stored_uuid}_assays_merged.pq"
    file_storage.save_file(saved_name, assays_merged_df.reset_index().to_parquet())

    return html.Div(
        children=[
            make_file_list_component(filenames, [], 1),
        ],
    )


# === STAGE 2 ===


def on_projections_visualization_entry(
    current_stage: int,
    stored_uuid: str,
    file_storage: FileStorage,
) -> go.Figure:
    """
    Callback for projections visualization stage entry.
    It loads the data from the storage, computes and visualizes the projections.

    :param current_stage: index of the current stage
    :param stored_uuid: session uuid
    :param file_storage: file storage
    :return: figure with projections
    """
    if current_stage != 1:
        return no_update

    load_name = f"{stored_uuid}_assays_merged.pq"
    merged_df = pd.read_parquet(pa.BufferReader(file_storage.read_file(load_name)))

    assays_preprocessor = MergedAssaysPreprocessor()
    assays_preprocessor.set_compounds_df(merged_df)

    # TODO: include both ACT/INH
    projection_columns = [
        col for col in merged_df.columns if "ACTIVATION" in col.upper()
    ]
    assays_preprocessor.set_columns_for_projection(projection_columns)

    for projector, name in PROJECTION_SETUP:
        assays_preprocessor.apply_projection(projector, name)

    saved_name = f"{stored_uuid}_assays_projection.pq"
    projections_df = assays_preprocessor.get_processed_df()
    file_storage.save_file(
        saved_name, projections_df.reset_index(drop=True).to_parquet()
    )

    #  TODO: include both ACT/INH
    activation_columns = [col for col in projections_df.columns if "ACTIVATION" in col]
    dropdown_options = []
    for value in activation_columns:
        option = {"label": value, "value": value}
        dropdown_options.append(option)

    fig = plot_projection_2d(projections_df, activation_columns[0], "UMAP")
    projections_df = eos_to_ecbd_link(projections_df)
    table = table_from_df(projections_df, "projection-table")

    attribute_options = html.Div(
        children=[
            dcc.Dropdown(
                id="projection-attribute-selection-box",
                options=dropdown_options,
                value=activation_columns[0],
                searchable=False,
                clearable=False,
                disabled=False,
            ),
        ]
    )

    method_options = html.Div(
        children=[
            dcc.Dropdown(
                id="projection-method-selection-box",
                options=[
                    {"label": "UMAP", "value": "UMAP"},
                    {"label": "PCA", "value": "PCA"},
                ],
                value="UMAP",
                searchable=False,
                clearable=False,
                disabled=False,
            ),
        ]
    )

    return (fig, table, attribute_options, method_options)


def on_dropdown_change(
    method: str, attribute: str, stored_uuid: str, file_storage: FileStorage
) -> go.Figure:
    """
    Callback for dropdown change. It loads the data from the storage and visualizes the projections.

    :param method: projection method
    :param attribute: projection attribute
    :param stored_uuid: session uuid
    :param file_storage: file storage
    :return: figure with projections"""

    load_name = f"{stored_uuid}_assays_projection.pq"
    projections_df = pd.read_parquet(pa.BufferReader(file_storage.read_file(load_name)))
    fig = plot_projection_2d(projections_df, attribute, method)
    return fig


def on_save_projections_click(
    n_clicks: int,
    stored_uuid: str,
    file_storage: FileStorage,
) -> None:
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
        Input("upload-projection-data", "contents"),
        Input("upload-projection-data", "filename"),
        Input("upload-projection-data", "last_modified"),
        State("user-uuid", "data"),
    )(functools.partial(on_projection_files_upload, file_storage=file_storage))
    callback(
        Output("projection-plot", "figure", allow_duplicate=True),
        Output("projection-table", "children"),
        Output("projection-attribute-selection-box", "children"),
        Output("projection-method-selection-box", "children"),
        Input(elements["STAGES_STORE"], "data"),
        State("user-uuid", "data"),
        prevent_initial_call=True,
    )(functools.partial(on_projections_visualization_entry, file_storage=file_storage))
    callback(
        Output("projection-plot", "figure", allow_duplicate=True),
        Input("projection-method-selection-box", "value"),
        Input("projection-attribute-selection-box", "value"),
        State("user-uuid", "data"),
        prevent_initial_call=True,
    )(functools.partial(on_dropdown_change, file_storage=file_storage))
    callback(
        Output("download-projections-csv", "data"),
        Input("save-projections-button", "n_clicks"),
        State("user-uuid", "data"),
        prevent_initial_call=True,
    )(functools.partial(on_save_projections_click, file_storage=file_storage))
