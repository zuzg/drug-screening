import io
import base64
import functools
import uuid
import numpy as np
import pandas as pd
import pyarrow as pa
import plotly.graph_objects as go

from dash import html, no_update, callback, Output, Input, State, callback_context

from dashboard.data.bmg_plate import parse_bmg_files
from dashboard.data.file_preprocessing.echo_files_parser import EchoFilesParser
from dashboard.storage import FileStorage
from dashboard.visualization.plots import visualize_multiple_plates


# === STAGE 1 ===


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


# === STAGE 2 ===

DISPLAYED_PLATES = 9
DIM = int(np.ceil(np.sqrt(DISPLAYED_PLATES)))


def on_heatmap_controls_clikced(
    n_clicks_prev: int,
    n_clicks_next: int,
    current_index: int,
    max_index: int,
) -> int:
    triggered = callback_context.triggered[0]["prop_id"].split(".")[0]
    if triggered == "heatmap-previous-btn":
        return max(0, current_index - DISPLAYED_PLATES)
    if triggered == "heatmap-next-btn" and current_index < max_index:
        return current_index + DISPLAYED_PLATES
    return no_update


def on_outlier_purge_stage_entry(
    current_stage: int,
    heatmap_start_index: int,
    stored_uuid: str,
    file_storage: FileStorage,
) -> tuple[go.Figure, int, str]:
    if current_stage != 1:
        return no_update
    raw_bmg = file_storage.read_file(f"{stored_uuid}_bmg_df.pq")
    bmg_df = pd.read_parquet(pa.BufferReader(raw_bmg))
    raw_vals = file_storage.read_file(f"{stored_uuid}_bmg_val.npz")
    bmg_vals = np.load(io.BytesIO(raw_vals))["arr_0"]
    vis_bmg_df = bmg_df.iloc[
        heatmap_start_index : heatmap_start_index + DISPLAYED_PLATES, :
    ]
    vis_bmg_vals = bmg_vals[
        heatmap_start_index : heatmap_start_index + DISPLAYED_PLATES
    ]
    fig = visualize_multiple_plates(vis_bmg_df, vis_bmg_vals, DIM, DIM)
    index_text = f"{heatmap_start_index + 1} - {heatmap_start_index + DISPLAYED_PLATES} / {bmg_vals.shape[0]}"
    return fig, max(0, bmg_vals.shape[0] - DISPLAYED_PLATES), index_text


# === STAGE 3 ===


# === STAGE 4 ===


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


# === STAGE 5 ===


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
        Output("heatmap-start-index", "data"),
        Input("heatmap-previous-btn", "n_clicks"),
        Input("heatmap-next-btn", "n_clicks"),
        State("heatmap-start-index", "data"),
        State("max-heatmap-index", "data"),
    )(on_heatmap_controls_clikced)

    callback(
        Output("plates-heatmap-graph", "figure"),
        Output("max-heatmap-index", "data"),
        Output("heatmap-index-display", "children"),
        Input(elements["STAGES_STORE"], "data"),
        Input("heatmap-start-index", "data"),
        State("user-uuid", "data"),
    )(functools.partial(on_outlier_purge_stage_entry, file_storage=file_storage))

    callback(
        Output("echo-filenames", "children"),
        Input("upload-echo-data", "contents"),
        Input("upload-echo-data", "filename"),
        Input("upload-echo-data", "last_modified"),
        State("user-uuid", "data"),
    )(functools.partial(upload_echo_data, file_storage=file_storage))
