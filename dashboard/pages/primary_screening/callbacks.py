from dash import html, no_update, callback, Output, Input, State

from ..error import throwable, DashboardError
from ...data.bmg_plate import parse_bmg_files_from_iostring
from ...storage import FileStorage
import io
import base64
import functools
import uuid

# ==== upload_stage callbacks ====
def validate_content(contents, filenames):
    if any(filename[-4:] != "txt" for filename in filenames):
        raise DashboardError("No txt files are not allowed")


@throwable(1)
def upload_data(contents, names, last_modified, stored_uuid, file_storage):
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
        [
            html.Div(
                [
                    html.H5("Loaded files"),
                    html.Hr(),
                    html.Ul(children=[html.Li(i) for i in names]),
                    html.Hr(),
                ]
            ),
            stored_uuid,
        ]
    )


def register_callbacks(elements, file_storage):
    callback(
        [
            Output("filenames", "children"),
            Output("user-uuid", "data"),
        ],
        Input("upload-data", "contents"),
        Input("upload-data", "filename"),
        Input("upload-data", "last_modified"),
        State("user-uuid", "data"),
        prevent_initial_call=True,
    )(functools.partial(upload_data, file_storage=file_storage))

    