from dash import html, no_update, callback, Output, Input, State

from ..error import throwable, DashboardError
from ...data.bmg_plate import parse_bmg_files_from_iostring
from ...storage import FileStorage
from ...data.file_preprocessing.echo_files_parser import EchoFilesParser
import io
import base64
import functools
import uuid

# ==== upload_stage callbacks ====
def validate_content(contents, filenames):
    if any(filename[-4:] != "txt" for filename in filenames):
        raise DashboardError("No txt files are not allowed")


@throwable(1)
def upload_bmg_data(contents, names, last_modified, stored_uuid, file_storage):
    if contents is None:
        return no_update
    #validate_content(contents, filenames)

    if not stored_uuid:
        stored_uuid = str(uuid.uuid4())

    bmg_files = []

    for content, filename in zip(contents, names):
        name, extension = filename.split(".")
        if extension == "txt":
            _, content_string = content.split(",")
            decoded = base64.b64decode(content_string)
            bmg_files.append((filename, io.StringIO(decoded.decode("utf-8"))))
    
    if(len(bmg_files)):
        bmg_df, val = parse_bmg_files_from_iostring(bmg_files)

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

@throwable(1)
def upload_echo_data(contents, names, last_modified, stored_uuid, file_storage):
    if contents is None:
        return no_update
    #validate_content(contents, filenames)

    if not stored_uuid:
        stored_uuid = str(uuid.uuid4())

    echo_files = []

    for content, filename in zip(contents, names):
        name, extension = filename.split(".")
        if extension == "csv":
            _, content_string = content.split(",")
            decoded = base64.b64decode(content_string)
            echo_files.append((filename, io.StringIO(decoded.decode("utf-8"))))
    
    if(len(echo_files)):
        echo_parser = EchoFilesParser()
        echo_parser.parse_files_iostring(echo_files)
        echo_df = echo_parser.echo_df
        exceptions_df = echo_parser.exceptions_df
        print(echo_df)
        serialized_processed_df = echo_df.reset_index().to_parquet()
        file_storage.save_file(f"{stored_uuid}_echo_df.pq", serialized_processed_df)
        serialized_processed_exceptions_df = exceptions_df.reset_index().to_parquet()
        file_storage.save_file(f"{stored_uuid}_exceptions_df.pq", serialized_processed_exceptions_df)

    return html.Div(
                [
                    html.H5("Loaded files"),
                    html.Hr(),
                    html.Ul(children=[html.Li(i) for i in names]),
                    html.Hr(),
                ]
            )
    


def register_callbacks(elements, file_storage):
    callback(
        [
            Output("bmg-filenames", "children"),
            Output("user-uuid", "data"),
            Output("dummy", "children")
        ],
        Input("upload-bmg-data", "contents"),
        Input("upload-bmg-data", "filename"),
        Input("upload-bmg-data", "last_modified"),
        State("user-uuid", "data"),
        prevent_initial_call=True,
    )(functools.partial(upload_bmg_data, file_storage=file_storage))
    callback(
        Output("echo-filenames", "children"),
        Input("upload-echo-data", "contents"),
        Input("upload-echo-data", "filename"),
        Input("upload-echo-data", "last_modified"),
        State("user-uuid", "data"),
        prevent_initial_call=True,
    )(functools.partial(upload_echo_data, file_storage=file_storage))

    