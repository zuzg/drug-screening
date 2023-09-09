import base64
import io
import uuid
import functools

import pandas as pd

from dash import Input, Output, State, callback, html, no_update

from dashboard.storage import FileStorage


# === STAGE 1 ===

EXPECTED_COLUMNS = {
    "CMPD ID",
    "Source Plate Barcode",
    "Source Well",
    "Destination Plate Barcode",
    "Destination Well",
    "Actual Volume",
    "% ACTIVATION",
    "% INHIBITION",
    "Z-SCORE",
}


def on_file_upload(content: str | None, stored_uuid: str, file_storage: FileStorage):
    """
    Callback for file upload. It saves the file to the storage and returns an icon
    indicating the status of the upload.

    :param content: base64 encoded file content
    :param stored_uuid: session uuid
    :param file_storage: file storage
    :return: icon indicating the status of the upload
    """
    if content is None:
        return no_update
    if stored_uuid is None:
        stored_uuid = str(uuid.uuid4())
    decoded = base64.b64decode(content.split(",")[1]).decode("utf-8")
    screen_df = pd.read_csv(io.StringIO(decoded))
    column_set = set(screen_df.columns)

    if missing_columns := (EXPECTED_COLUMNS - column_set):
        missing_message = ", ".join(sorted(missing_columns))
        return html.Div(
            children=[
                html.I(className="fas fa-times-circle text-danger me-2"),
                html.Span(
                    children=[
                        f"File does not contain the expected columns: ",
                        html.Span(missing_message, className="fw-bold"),
                    ]
                ),
            ],
            className="text-danger",
        )

    compounds_count = len(screen_df["CMPD ID"].unique())
    saved_name = f"{stored_uuid}_screening.pq"
    file_storage.save_file(saved_name, screen_df.to_parquet())

    return html.Div(
        children=[
            html.I(className="fas fa-check-circle text-success me-2"),
            html.Span(
                children=[
                    f"File uploaded successfully. Found ",
                    html.Span(compounds_count, className="fw-bold"),
                    " compounds.",
                ]
            ),
        ],
        className="text-success",
    )


def register_callbacks(elements, file_storage: FileStorage):
    callback(
        Output("screening-file-message", "children"),
        Input("upload-screening-data", "contents"),
        State("user-uuid", "data"),
    )(functools.partial(on_file_upload, file_storage=file_storage))
