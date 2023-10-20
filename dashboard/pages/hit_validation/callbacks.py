import base64
import io
import uuid
import functools
import json
import pandas as pd
import pyarrow as pa

from datetime import datetime

from dash import (
    Input,
    Output,
    State,
    callback,
    html,
    no_update,
    ALL,
    callback_context,
    dcc,
)

from dashboard.storage import FileStorage
from dashboard.data.determination import perform_hit_determination
from dashboard.visualization.plots import plot_ic50

SCREENING_FILENAME = "{0}_screening_df.pq"
HIT_FILENAME = "{0}_hit_df.pq"


# === STAGE 1 ===
def on_file_upload(
    content: str | None,
    stored_uuid: str,
    concentration_lower_bound: float,
    concentration_upper_bound: float,
    file_storage: FileStorage,
) -> tuple[html.Div, str]:
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
        return no_update, no_update
    if stored_uuid is None:
        stored_uuid = str(uuid.uuid4())

    decoded = base64.b64decode(content.split(",")[1]).decode("utf-8")
    screen_df = pd.read_csv(io.StringIO(decoded), delimiter=";")
    if screen_df.shape[1] == 1:
        screen_df = pd.read_csv(io.StringIO(decoded), delimiter=",")
    screen_df = screen_df.rename(str.upper, axis="columns")

    rename_dict = {}
    for column in screen_df.columns:
        if column.startswith("CONCENTRATION"):
            rename_dict[column] = "CONCENTRATION"
        elif column.startswith("INHIBITION"):
            rename_dict[column] = "VALUE"
        elif column.startswith("ACTIVATION"):
            rename_dict[column] = "VALUE"

    screen_df = screen_df.rename(rename_dict, axis=1)
    column_set = set(screen_df.columns)

    missing = []
    if "EOS" not in column_set:
        missing.append("column EOS")
    if "CONCENTRATION" not in column_set:
        missing.append("column starting with 'concentration'")
    if "VALUE" not in column_set:
        missing.append("column starting with 'activation' or 'inhibition'")

    if missing:
        missing_message = ", ".join(sorted(missing))
        return (
            html.Div(
                children=[
                    html.I(className="fas fa-times-circle text-danger me-2"),
                    html.Span(
                        children=[
                            f"File does not contain the following: ",
                            html.Span(missing_message, className="fw-bold"),
                        ]
                    ),
                ],
                className="text-danger",
            ),
            stored_uuid,
        )

    # screening df needs to be safed for plots
    file_storage.save_file(
        SCREENING_FILENAME.format(stored_uuid), screen_df.to_parquet(index=False)
    )
    compounds_count = len(screen_df["EOS"].unique())
    saved_name = HIT_FILENAME.format(stored_uuid)

    # Placeholder for hit determination
    hit_determination_df = perform_hit_determination(
        screen_df, concentration_lower_bound, concentration_upper_bound
    )
    unfit = hit_determination_df.EOS[hit_determination_df.ic50.isna()].tolist()

    file_storage.save_file(saved_name, hit_determination_df.to_parquet())

    result_msg = html.Div(
        children=[
            html.Div(
                children=[
                    html.I(className="fas fa-check-circle me-2"),
                    html.Span(
                        children=[
                            f"File uploaded successfully. Found ",
                            html.Span(compounds_count, className="fw-bold"),
                            " compounds.",
                        ],
                    ),
                ],
                className="text-success",
            ),
            html.Div(
                children=[
                    html.I(className="fas fa-exclamation-circle me-2"),
                    html.Span(
                        children=[
                            f"Found ",
                            html.Span(len(unfit), className="fw-bold"),
                            " compounds that failed curve fit: ",
                            html.Span(", ".join(unfit), className="fw-bold"),
                        ],
                    ),
                ],
                className="text-warning",
            ),
        ],
    )
    return result_msg, stored_uuid


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

    hit_determination_df = pd.read_parquet(
        pa.BufferReader(file_storage.read_file(HIT_FILENAME.format(stored_uuid)))
    )

    compounds_list = sorted(hit_determination_df["EOS"].unique().tolist())
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


activity_icons = {
    "active": html.I(className="fas fa-check-circle text-success"),
    "inactive": html.I(className="fas fa-times-circle text-danger"),
    "inconclusive": html.I(className="fas fa-question-circle text-warning"),
}


def on_selected_compound_changed(
    selected_compound: str,
    unstack_n_clicks: int,
    apply_n_clicks: int,
    top_override: float | None,
    bottom_override: float | None,
    stored_uuid: str,
    file_storage: FileStorage,
) -> html.Div:
    """
    Callback for selected compound change. It loads the data from the storage and
    returns the data for the compound.

    :param selected_compound: selected compound
    :param unstack_n_clicks: number of clicks on the unstack button
    :param apply_n_clicks: number of clicks on the apply button
    :param top_override: top override
    :param bottom_override: bottom override
    :param stored_uuid: session uuid
    :param file_storage: file storage
    :return: data for the compound
    """
    # if unstack clicked, reset overrides
    hit_load_name = HIT_FILENAME.format(stored_uuid)
    hit_determination_df = pd.read_parquet(
        pa.BufferReader(file_storage.read_file(hit_load_name))
    )
    screening_load_name = SCREENING_FILENAME.format(stored_uuid)
    screening_data = pd.read_parquet(
        pa.BufferReader(file_storage.read_file(screening_load_name))
    ).loc[lambda df: df["EOS"] == selected_compound]
    concentrations = screening_data["CONCENTRATION"].to_numpy()
    values = screening_data["VALUE"].to_numpy()

    entry = (
        hit_determination_df[hit_determination_df["EOS"] == selected_compound]
        .iloc[0]
        .to_dict()
    )
    index = hit_determination_df.index[
        hit_determination_df["EOS"] == selected_compound
    ][0]
    trigger = callback_context.triggered[0]["prop_id"]
    unstack_clicked = trigger == "hit-browser-unstack-button.n_clicks"
    apply_clicked = trigger == "hit-browser-apply-button.n_clicks"
    if unstack_clicked:
        top_override = entry["upper_limit"]
        bottom_override = entry["lower_limit"]
    if unstack_clicked or apply_clicked:
        hit_determination_df.loc[index, "TOP"] = top_override
        hit_determination_df.loc[index, "BOTTOM"] = bottom_override
        entry["TOP"] = top_override
        entry["BOTTOM"] = bottom_override

    if unstack_clicked or apply_clicked:
        file_storage.save_file(hit_load_name, hit_determination_df.to_parquet())

    graph = plot_ic50(entry, concentrations, values)

    result = {
        "id": entry["EOS"],
        "min-modulation": round(entry["min_value"], 5),
        "max-modulation": round(entry["max_value"], 5),
        "ic50": round(entry["ic50"], 5),
        "curve-slope": round(entry["slope"], 5),
        "r2": round(entry["r2"] * 100, 5),
        "is-active": html.Span(
            children=[
                activity_icons[entry["activity_final"]],
                html.Span(entry["activity_final"].upper(), className="ms-1"),
            ]
        ),
        "graph": graph,
        "top": round(entry["TOP"], 5),
        "bottom": round(entry["BOTTOM"], 5),
    }
    return tuple(result.values())


# === STAGE 3 ===


def on_json_generate_button_click(
    n_clicks,
    correlation_plots_report,
    file_storage: FileStorage,
):
    filename = f"hit_validation_settings_{datetime.now().strftime('%Y-%m-%d')}.json"
    json_object = json.dumps(correlation_plots_report, indent=4)
    return dict(content=json_object, filename=filename)


def on_download_summary_csv_button_click(
    n_clicks,
    stored_uuid: str,
    file_storage: FileStorage,
):
    """
    Callback for download summary csv button click. It loads the data from the storage
    and returns the data for the compound.

    :param n_clicks: number of clicks
    :param stored_uuid: session uuid
    :param file_storage: file storage
    :return: hit determination data in csv format
    """
    filename = f"hit_validation_summary_{datetime.now().strftime('%Y-%m-%d')}.csv"
    hit_df = pd.read_parquet(
        pa.BufferReader(file_storage.read_file(HIT_FILENAME.format(stored_uuid)))
    )

    return dcc.send_data_frame(hit_df.to_csv, filename)


def register_callbacks(elements, file_storage: FileStorage):
    callback(
        Output("screening-file-message", "children"),
        Output("user-uuid", "data", allow_duplicate=True),
        Input("upload-screening-data", "contents"),
        State("user-uuid", "data"),
        State("concentration-lower-bound-store", "data"),
        State("concentration-upper-bound-store", "data"),
        prevent_initial_call="initial_duplicate",
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
        Output("hit-browser-top", "value"),
        Output("hit-browser-bottom", "value"),
        Input("selected-compound-store", "data"),
        Input("hit-browser-unstack-button", "n_clicks"),
        Input("hit-browser-apply-button", "n_clicks"),
        State("hit-browser-top", "value"),
        State("hit-browser-bottom", "value"),
        State("user-uuid", "data"),
    )(functools.partial(on_selected_compound_changed, file_storage=file_storage))

    callback(
        Output("download-json-settings-hit-validation", "data"),
        Input("generate-json-button", "n_clicks"),
        State("report-data-hit-validation-input", "data"),
        prevent_initial_call=True,
    )(functools.partial(on_json_generate_button_click, file_storage=file_storage))

    callback(
        Output("download-csv-summary-hit-validation", "data"),
        Input("download-csv-summary-hit-validation-button", "n_clicks"),
        State("user-uuid", "data"),
        prevent_initial_call=True,
    )(
        functools.partial(
            on_download_summary_csv_button_click, file_storage=file_storage
        )
    )
