from dash import Dash
from dash.dependencies import Input, Output, State

from .upload import update_output


def register_callbacks(app: Dash) -> None:
    app.callback(
        Output("output-data-upload", "children"),
        Input("upload-data", "contents"),
        State("upload-data", "filename"),
        State("upload-data", "last_modified"),
    )(update_output)
