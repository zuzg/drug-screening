import uuid
import functools
import base64
import io

import pandas as pd
import pyarrow as pa

from plotly import graph_objects as go
from plotly import express as px
from dash import Input, Output, State, callback, html, no_update
from dashboard.data import validation
from dashboard.storage import FileStorage

# === STAGE 1 ===

ICON_OK = html.I(
    className="fa-solid fa-circle-check",
    style={"color": "green", "margin-right": "0.5rem"},
)

ICON_ERROR = html.I(
    className="fa-solid fa-circle-xmark",
    style={"color": "red", "margin-right": "0.5rem"},
)

SUFFIX_CORR_FILE1 = "corr_file1"
SUFFIX_CORR_FILE2 = "corr_file2"


def on_file_upload(
    content: str | None, stored_uuid: str, file_storage: FileStorage, store_suffix: str
):
    """
    Callback for file upload. It saves the file to the storage and returns an icon
    indicating the status of the upload.

    :param content: base64 encoded file content
    :param stored_uuid: session uuid
    :param file_storage: file storage
    :param store_suffix: suffix for the file name
    :return: icon indicating the status of the upload
    """
    if content is None:
        return no_update
    if stored_uuid is None:
        stored_uuid = str(uuid.uuid4())

    decoded = base64.b64decode(content.split(",")[1]).decode("utf-8")
    try:
        corr_df = pd.read_csv(io.StringIO(decoded))
        validation.validate_correlation_dataframe(corr_df)
    except Exception as e:
        return ICON_ERROR

    saved_name = f"{stored_uuid}_{store_suffix}.pq"

    file_storage.save_file(saved_name, corr_df.to_parquet())

    return ICON_OK


def on_both_files_uploaded(
    content1: str | None,
    content2: str | None,
    stored_uuid: str,
    file_storage: FileStorage,
):
    """
    Callback for checking if both files are uploaded and compatible.

    :param content1: base64 encoded file 1 content
    :param content2: base64 encoded file 2 content
    :param stored_uuid: session uuid
    :param file_storage: file storage
    :return: icon indicating the status of compatibility
    """
    if content1 is None or content2 is None:
        return no_update

    if stored_uuid is None:
        stored_uuid = str(uuid.uuid4())

    saved_name_1 = f"{stored_uuid}_{SUFFIX_CORR_FILE1}.pq"
    saved_name_2 = f"{stored_uuid}_{SUFFIX_CORR_FILE2}.pq"

    try:
        corr_df_1 = pd.read_parquet(
            pa.BufferReader(file_storage.read_file(saved_name_1))
        )
        corr_df_2 = pd.read_parquet(
            pa.BufferReader(file_storage.read_file(saved_name_2))
        )
        validation.validate_correlation_dfs_compatible(corr_df_1, corr_df_2)
    except Exception as e:
        return ICON_ERROR

    return ICON_OK


# === STAGE 2 ===


def on_visualization_stage_entry(
    current_stage: int, stored_uuid: str, file_storage: FileStorage
) -> tuple[go.Figure, go.Figure]:
    """
    Callback for visualization stage entry. It loads the data from the storage and
    returns the figures.

    :param current_stage: current stage number
    :param stored_uuid: session uuid
    :param file_storage: file storage
    :return: figures
    """
    if current_stage != 1 or stored_uuid is None:
        return no_update, no_update

    saved_name_1 = f"{stored_uuid}_{SUFFIX_CORR_FILE1}.pq"
    saved_name_2 = f"{stored_uuid}_{SUFFIX_CORR_FILE2}.pq"

    corr_df_1 = pd.read_parquet(pa.BufferReader(file_storage.read_file(saved_name_1)))
    corr_df_2 = pd.read_parquet(pa.BufferReader(file_storage.read_file(saved_name_2)))

    # TODO: implement visualization
    inhibition_fig = px.scatter([1, 2, 3, 4, 5], [1, 2, 3, 4, 5])
    concentration_fig = px.scatter([1, 2, 3, 4, 5], [1, 2, 3, 4, 5])

    return inhibition_fig, concentration_fig


def register_callbacks(elements, file_storage: FileStorage):
    callback(
        Output("file-1-status", "children"),
        Input("upload-file-1", "contents"),
        State("user-uuid", "data"),
    )(
        functools.partial(
            on_file_upload, file_storage=file_storage, store_suffix=SUFFIX_CORR_FILE1
        )
    )

    callback(
        Output("file-2-status", "children"),
        Input("upload-file-2", "contents"),
        State("user-uuid", "data"),
    )(
        functools.partial(
            on_file_upload, file_storage=file_storage, store_suffix=SUFFIX_CORR_FILE2
        )
    )

    callback(
        Output("compatibility-status", "children"),
        Input("upload-file-1", "contents"),
        Input("upload-file-2", "contents"),
        State("user-uuid", "data"),
    )(functools.partial(on_both_files_uploaded, file_storage=file_storage))

    callback(
        Output("inhibition-graph", "figure"),
        Output("concentration-graph", "figure"),
        Input(elements["STAGES_STORE"], "data"),
        State("user-uuid", "data"),
    )(functools.partial(on_visualization_stage_entry, file_storage=file_storage))