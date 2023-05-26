import base64
import functools
import io
import uuid

import numpy as np
import pandas as pd
import plotly.graph_objects as go
import pyarrow as pa
from dash import Input, Output, State, callback, html, no_update

from dashboard.data.bmg_plate import parse_bmg_files
from dashboard.data.file_preprocessing.echo_files_parser import EchoFilesParser
from dashboard.storage import FileStorage

from ...data.bmg_plate import parse_bmg_files
from ...data.file_preprocessing.echo_files_parser import EchoFilesParser


def upload_bmg_data(contents, names, last_modified, stored_uuid, file_storage):
    if contents is None:
        return no_update

    if not stored_uuid:
        stored_uuid = str(uuid.uuid4())

    bmg_files = []

    for content, filename in zip(contents, names):
        name, extension = filename.split(".")
        if extension == "txt":
            _, content_string = content.split(",")
            decoded = base64.b64decode(content_string)
            bmg_files.append((filename, io.StringIO(decoded.decode("utf-8"))))

    if bmg_files:
        bmg_df, val = parse_bmg_files(tuple(bmg_files))
        stream = io.BytesIO()
        np.savez_compressed(stream, val)
        stream.seek(0)
        file_storage.save_file(f"{stored_uuid}_bmg_val.npz", stream.read())
        serialized_processed_df = bmg_df.reset_index().to_parquet()
        file_storage.save_file(f"{stored_uuid}_bmg_df.pq", serialized_processed_df)

    return (
        html.Div(
            [
                html.H5("Loaded files"),
                html.Hr(),
                html.Ul(children=[html.Li(i) for i in names]),
                html.Hr(),
            ]
        ),
        stored_uuid,
    )


def upload_echo_data(contents, names, last_modified, stored_uuid, file_storage):
    if contents is None:
        return no_update

    echo_files = []

    for content, filename in zip(contents, names):
        name, extension = filename.split(".")
        if extension == "csv":
            _, content_string = content.split(",")
            decoded = base64.b64decode(content_string)
            echo_files.append((filename, io.StringIO(decoded.decode("utf-8"))))

    if echo_files:
        echo_parser = EchoFilesParser()
        echo_parser.parse_files(tuple(echo_files)).retain_key_columns()
        echo_df = echo_parser.get_processed_echo_df()
        exceptions_df = echo_parser.get_processed_exception_df()
        serialized_processed_df = echo_df.reset_index().to_parquet()
        file_storage.save_file(f"{stored_uuid}_echo_df.pq", serialized_processed_df)
        serialized_processed_exceptions_df = exceptions_df.reset_index().to_parquet()
        file_storage.save_file(
            f"{stored_uuid}_exceptions_df.pq", serialized_processed_exceptions_df
        )

    return html.Div(
        [
            html.H5("Loaded files"),
            html.Hr(),
            html.Ul(children=[html.Li(i) for i in names]),
            html.Hr(),
        ]
    )


# === STAGE 5 ===


def on_stage_5_entry(current_stage: int, stored_uuid: str, file_storage: FileStorage):
    if current_stage != 4:
        return no_update
    echo_df = pd.read_parquet(
        pa.BufferReader(file_storage.read_file(f"{stored_uuid}_echo_df.pq"))
    )
    return (
        html.Div(
            [
                html.H5("STAGE 5 ECHO FILES"),
            ]
        ),
        echo_df,
    )


def register_callbacks(elements, file_storage):
    callback(
        [
            Output("bmg-filenames", "children"),
            Output("user-uuid", "data"),
        ],
        Input("upload-bmg-data", "contents"),
        Input("upload-bmg-data", "filename"),
        Input("upload-bmg-data", "last_modified"),
        State("user-uuid", "data"),
    )(functools.partial(upload_bmg_data, file_storage=file_storage))
    callback(
        Output("echo-filenames", "children"),
        Input("upload-echo-data", "contents"),
        Input("upload-echo-data", "filename"),
        Input("upload-echo-data", "last_modified"),
        State("user-uuid", "data"),
    )(functools.partial(upload_echo_data, file_storage=file_storage))
    (functools.partial(upload_bmg_data, file_storage=file_storage))
    callback(
        Output("stage-5", "children"),
        Output("act-inh-table", "data"),
        Input(elements["STAGES_STORE"], "data"),
        State("user-uuid", "data"),
    )(functools.partial(on_stage_5_entry, file_storage=file_storage))
