import uuid
import functools
import base64
import io

import pandas as pd
import pyarrow as pa

from dash import Input, Output, State, callback, callback_context, html, no_update
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


def on_file_upload(content, stored_uuid, file_storage: FileStorage, store_suffix: str):
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


def on_both_files_uploaded(content1, content2, stored_uuid, file_storage: FileStorage):
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
