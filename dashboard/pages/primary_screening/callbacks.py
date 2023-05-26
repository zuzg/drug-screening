import io
import base64
import functools
import uuid
import numpy as np
from dash import html, no_update, callback, Output, Input, State
from dashboard.storage import FileStorage
import pandas as pd
import pyarrow as pa
import plotly.graph_objects as go

from dashboard.data.bmg_plate import parse_bmg_files
from dashboard.data.file_preprocessing.echo_files_parser import EchoFilesParser
from dashboard.visualization.plots import (
    plot_control_values,
    plot_row_col_means,
    plot_z_per_plate,
)


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
        echo_parser.parse_files(tuple(echo_files))
        echo_df = echo_parser.echo_df
        exceptions_df = echo_parser.exceptions_df
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


# === STAGE 3 ===


def on_stage_3_entry(
    current_stage: int, stored_uuid: str, file_storage: FileStorage
) -> tuple[go.Figure]:
    if current_stage != 2:
        return no_update
    raw_bmg = file_storage.read_file(f"{stored_uuid}_bmg_df.pq")
    bmg_df = pd.read_parquet(pa.BufferReader(raw_bmg))
    raw_vals = file_storage.read_file(f"{stored_uuid}_bmg_val.npz")
    bmg_vals = np.load(io.BytesIO(raw_vals))["arr_0"]
    control_values_fig = plot_control_values(bmg_df)
    row_col_fig = plot_row_col_means(bmg_vals)
    z_fig = plot_z_per_plate(bmg_df.barcode, bmg_df.z_factor)
    return control_values_fig, row_col_fig, z_fig


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
        Output("control-values", "figure"),
        Output("mean-cols-rows", "figure"),
        Output("z-per-plate", "figure"),
        Input(elements["STAGES_STORE"], "data"),
        State("user-uuid", "data"),
    )(functools.partial(on_stage_3_entry, file_storage=file_storage))
    callback(
        Output("echo-filenames", "children"),
        Input("upload-echo-data", "contents"),
        Input("upload-echo-data", "filename"),
        Input("upload-echo-data", "last_modified"),
        State("user-uuid", "data"),
    )(functools.partial(upload_echo_data, file_storage=file_storage))
