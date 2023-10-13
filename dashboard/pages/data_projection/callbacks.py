import base64
import functools
import io
import uuid

import pandas as pd
import plotly.graph_objects as go
import pyarrow as pa
from dash import Input, Output, State, callback, dash_table, html, no_update
from sklearn.decomposition import PCA
from umap import UMAP

from dashboard.data.preprocess import MergedAssaysPreprocessor
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
            html.I(className="fas fa-check-circle text-success me-2"),
            html.P("Files uploaded successfully."),
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

    # TODO: allow for ACT/INH selection
    projection_columns = [
        col for col in merged_df.columns if "ACTIVATION" in col.upper()
    ]
    assays_preprocessor.set_columns_for_projection(projection_columns)

    for projector, name in PROJECTION_SETUP:
        assays_preprocessor.apply_projection(projector, name)

    saved_name = f"{stored_uuid}_assays_projection.pq"
    projections_df = assays_preprocessor.get_processed_df()
    file_storage.save_file(saved_name, projections_df.reset_index().to_parquet())
    # table_columns = [col for col in projections_df.columns if col == "EOS" or col.endswith("X") or col.endswith("Y")]

    # TEST
    fig = plot_projection_2d(projections_df, "% ACTIVATION experiment2", "PCA")
    table = table_from_df(projections_df, "projection-table")

    return fig, table


# projections_df.to_dict("records"), [i for i in projections_df.columns]


def register_callbacks(elements, file_storage: FileStorage):
    callback(
        Output("projections-file-message", "children"),
        Input("upload-projection-data", "contents"),
        Input("upload-projection-data", "filename"),
        Input("upload-projection-data", "last_modified"),
        State("user-uuid", "data"),
    )(functools.partial(on_projection_files_upload, file_storage=file_storage))
    callback(
        Output("projection-plot", "figure"),  # , allow_duplicate=True),
        Output("projection-table", "children"),
        Input(elements["STAGES_STORE"], "data"),
        State("user-uuid", "data"),
    )(functools.partial(on_projections_visualization_entry, file_storage=file_storage))
