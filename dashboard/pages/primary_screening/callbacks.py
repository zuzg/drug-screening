import base64
import functools
import io
import uuid

import numpy as np
import pandas as pd
import plotly.graph_objects as go
import pyarrow as pa
from dash import Input, Output, Patch, State, callback, dcc, html, no_update

from dashboard.data.bmg_plate import parse_bmg_files
from dashboard.data.combine import combine_bmg_echo_data, split_compounds_controls
from dashboard.data.file_preprocessing.echo_files_parser import EchoFilesParser
from dashboard.storage import FileStorage
from dashboard.visualization.plots import visualize_activation_inhibition_zscore

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
    echo_df["CMPD ID"] = "TODO"

    bmg_df = pd.read_parquet(
        pa.BufferReader(file_storage.read_file(f"{stored_uuid}_bmg_df.pq"))
    )
    bmg_vals = np.load(
        io.BytesIO(file_storage.read_file(f"{stored_uuid}_bmg_val.npz"))
    )["arr_0"]

    echo_bmg_combined = combine_bmg_echo_data(echo_df, bmg_df, bmg_vals)
    compounds_df, control_pos_df, control_neg_df = split_compounds_controls(
        echo_bmg_combined
    )

    echo_bmg_combined = (
        echo_bmg_combined.drop_duplicates()
    )  # TODO: inform the user about it/allow for deciding what to do

    echo_bmg_combined = echo_bmg_combined.reset_index().to_dict("records")

    fig_z_score = visualize_activation_inhibition_zscore(
        compounds_df, control_pos_df, control_neg_df, "Z-SCORE", (-3, 3)
    )

    fig_activation = visualize_activation_inhibition_zscore(
        compounds_df, control_pos_df, control_neg_df, "% ACTIVATION"
    )

    fig_inhibition = visualize_activation_inhibition_zscore(
        compounds_df, control_pos_df, control_neg_df, "% INHIBITION"
    )

    return echo_bmg_combined, fig_z_score, fig_activation, fig_inhibition


def on_z_score_range_update(min_value, max_value, figure):
    new_figure = go.Figure(figure)

    shapes = []
    annotations = []
    if min_value is not None and (max_value is None or min_value <= max_value):
        shapes.append(
            {
                "type": "line",
                "y0": min_value,
                "y1": min_value,
                "line": {
                    "color": "gray",
                    "width": 3,
                    "dash": "dash",
                },
            }
        )
        annotations.append(
            {
                "y": min_value,
                "text": f"MIN: {min_value:.2f}",
                "showarrow": False,
                "font": {"color": "gray"},
            }
        )

    if max_value is not None and (min_value is None or min_value <= max_value):
        shapes.append(
            {
                "type": "line",
                "y0": max_value,
                "y1": max_value,
                "line": {
                    "color": "gray",
                    "width": 3,
                    "dash": "dash",
                },
            }
        )
        annotations.append(
            {
                "x": 1,
                "xanchor": "right",
                "y": max_value,
                "text": f"MAX: {max_value:.2f}",
                "showarrow": False,
                "font": {"color": "gray"},
            }
        )

    new_figure.update_layout(shapes=shapes, annotations=annotations)
    return new_figure


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
        Output("echo-bmg-combined", "data"),
        Output("z-score-plot", "figure"),
        Output("activation-plot", "figure"),
        Output("inhibition-plot", "figure"),
        Input(elements["STAGES_STORE"], "data"),
        State("user-uuid", "data"),
    )(functools.partial(on_stage_5_entry, file_storage=file_storage))
    callback(
        Output("z-score-plot", "figure", allow_duplicate=True),
        [Input("input-z-score-min", "value"), Input("input-z-score-max", "value")],
        State("z-score-plot", "figure"),
        prevent_initial_call=True,
    )(functools.partial(on_z_score_range_update))
