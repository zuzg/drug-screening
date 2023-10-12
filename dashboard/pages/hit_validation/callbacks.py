import base64
import io
import uuid
import functools
from datetime import datetime
import json

import pandas as pd
import pyarrow as pa

from dash import Input, Output, State, callback, html, no_update, ALL, callback_context

from dashboard.storage import FileStorage
from dashboard.data.determination import perform_hit_determination
from dashboard.visualization.plots import plot_ic50


# === STAGE 1 ===

EXPECTED_COLUMNS = {
    "CMPD ID",
    # TODO: specify the expected columns
}


def on_file_upload(
    content: str | None,
    stored_uuid: str,
    concentration_lower_bound: float,
    concentration_upper_bound: float,
    file_storage: FileStorage,
) -> html.Div:
    """
    Callback for file upload. It saves the file to the storage and returns an icon
    indicating the status of the upload.

    :param content: base64 encoded file content
    :param stored_uuid: session uuid
    :param concentration_lower_bound: concentration lower bound
    :param concentration_upper_bound: concentration upper bound
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

    # Placeholder for hit determination
    hit_determination_df = perform_hit_determination(
        screen_df, concentration_lower_bound, concentration_upper_bound
    )

    file_storage.save_file(saved_name, hit_determination_df.to_parquet())

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


FAIL_BOUNDS_ELEMENT = html.Div(
    children=[
        html.I(className="fas fa-times-circle text-danger me-2"),
        html.Span(
            children=[
                "Lower bound cannot be greater than upper bound.",
            ]
        ),
    ],
    className="text-danger",
)


def on_concentration_bounds_change(
    lower_bound: float, upper_bound: float
) -> tuple[float, float, html.Div]:
    """
    Callback for concentration bounds change. It checks if the lower bound is greater
    than the upper bound.

    :param lower_bound: lower bound
    :param upper_bound: upper bound
    :return: icon indicating the status of the bounds
    """
    if lower_bound > upper_bound:
        return no_update, no_update, FAIL_BOUNDS_ELEMENT, {}
    report_data = {"lower_bound": lower_bound, "upper_bound": upper_bound}
    return lower_bound, upper_bound, "", report_data


# === STAGE 2 ===


def on_hit_browser_stage_entry(
    current_stage: int,
    stored_uuid: str,
    file_storage: FileStorage,
) -> tuple[list[html.Button], str]:
    """
    Callback for hit browser stage entry. It loads the data from the storage and
    Populates the compounds list.

    :param current_stage: index of the current stage
    :param stored_uuid: session uuid
    :param file_storage: file storage
    :return: list of buttons with compounds
    """
    if current_stage != 1:
        return no_update

    load_name = f"{stored_uuid}_screening.pq"
    hit_determination_df = pd.read_parquet(
        pa.BufferReader(file_storage.read_file(load_name))
    )

    compounds_list = sorted(hit_determination_df["CMPD ID"].unique().tolist())
    return [
        html.Button(
            compound,
            className="text-center font-monospace fw-semibold mb-1 btn btn-primary btn-sm",
            id={"type": "compound-button", "index": compound},
        )
        for compound in compounds_list
    ], compounds_list[0]


def on_compound_button_click(n_clicks: int, compound_id: str) -> str:
    """
    Callback for compound button click. It returns the compound name.

    :param compound: compound name
    :return: compound name
    """
    return callback_context.triggered_id["index"]


def on_selected_compound_changed(
    selected_compound: str,
    stored_uuid: str,
    file_storage: FileStorage,
) -> html.Div:
    load_name = f"{stored_uuid}_screening.pq"
    hit_determination_df = pd.read_parquet(
        pa.BufferReader(file_storage.read_file(load_name))
    )
    entry = (
        hit_determination_df[hit_determination_df["CMPD ID"] == selected_compound]
        .iloc[0]
        .to_dict()
    )
    # TODO: replace with real data
    graph = plot_ic50(entry)
    result = {
        "id": "Compound " + entry["CMPD ID"],
        "min-modulation": 0,
        "max-modulation": 100,
        "ic50": 0,
        "curve-slope": 0,
        "r2": 0,
        "is-active": html.I(className="fas fa-times-circle text-danger"),
        "graph": graph,
    }
    return tuple(result.values())


def on_json_generate_button_click(
    n_clicks,
    correlation_plots_report,
    file_storage: FileStorage,
):
    filename = f"hit_validation_settings_{datetime.now().strftime('%Y-%m-%d')}.json"
    json_object = json.dumps(correlation_plots_report, indent=4)
    return dict(content=json_object, filename=filename)


def register_callbacks(elements, file_storage: FileStorage):
    callback(
        Output("screening-file-message", "children"),
        Input("upload-screening-data", "contents"),
        State("user-uuid", "data"),
        State("concentration-lower-bound-store", "data"),
        State("concentration-upper-bound-store", "data"),
    )(functools.partial(on_file_upload, file_storage=file_storage))

    callback(
        Output("concentration-lower-bound-store", "data"),
        Output("concentration-upper-bound-store", "data"),
        Output("parameters-message", "children"),
        Output("report-data-hit-validation-input", "data"),
        Input("concentration-lower-bound-input", "value"),
        Input("concentration-upper-bound-input", "value"),
    )(on_concentration_bounds_change)

    callback(
        Output("compounds-list-container", "children"),
        Output("selected-compound-store", "data"),
        Input(elements["STAGES_STORE"], "data"),
        State("user-uuid", "data"),
    )(functools.partial(on_hit_browser_stage_entry, file_storage=file_storage))

    callback(
        Output("selected-compound-store", "data", allow_duplicate=True),
        Input({"type": "compound-button", "index": ALL}, "n_clicks"),
        State({"type": "compound-button", "index": ALL}, "id"),
        prevent_initial_call=True,
    )(on_compound_button_click)

    callback(
        Output("compound-id", "children"),
        Output("min-modulation-value", "children"),
        Output("max-modulation-value", "children"),
        Output("ic50-value", "children"),
        Output("curve-slope-value", "children"),
        Output("r2-value", "children"),
        Output("is-active-value", "children"),
        Output("hit-browser-plot", "figure"),
        Input("selected-compound-store", "data"),
        State("user-uuid", "data"),
    )(functools.partial(on_selected_compound_changed, file_storage=file_storage))

    callback(
        Output("download-json-settings-hit-validation", "data"),
        Input("generate-json-button", "n_clicks"),
        State("report-data-hit-validation-input", "data"),
        prevent_initial_call=True,
    )(functools.partial(on_json_generate_button_click, file_storage=file_storage))
