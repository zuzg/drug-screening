import base64
import dash_dangerously_set_inner_html as dhtml
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
from dashboard.data.determination import (
    perform_hit_determination,
    four_param_logistic,
    find_argument_four_param_logistic,
)
from dashboard.visualization.plots import plot_ic50
from dashboard.data.determination import perform_hit_determination
from dashboard.visualization.plots import plot_ic50, plot_smiles
from dashboard.pages.hit_validation.report.generate_jinja_report import (
    generate_jinja_report,
)

SCREENING_FILENAME = "{0}_screening_df.pq"
HIT_FILENAME = "{0}_hit_df.pq"


# === STAGE 1 ===
def on_file_upload(
    content: str | None,
    stored_uuid: str,
    concentration_lower_bound: float,
    concentration_upper_bound: float,
    top_lower_bound: float,
    top_upper_bound: float,
    file_storage: FileStorage,
) -> tuple[html.Div, str]:
    """
    Callback for file upload. It saves the file to the storage and returns an icon
    indicating the status of the upload.

    :param content: base64 encoded file content
    :param stored_uuid: session uuid
    :param concentration_lower_bound: concentration lower bound
    :param concentration_upper_bound: concentration upper bound
    :param top_lower_bound: top lower bound
    :param top_upper_bound: top upper bound
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
        screen_df,
        concentration_lower_bound,
        concentration_upper_bound,
        top_lower_bound,
        top_upper_bound,
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


def on_bounds_change(
    lower_bound: float, upper_bound: float
) -> tuple[float, float, html.Div]:
    """
    Callback for bounds change. It checks if the lower bound is greater
    than the upper bound.

    :param lower_bound: lower bound
    :param upper_bound: upper bound
    :return: icon indicating the status of the bounds
    """
    if lower_bound is None or upper_bound is None or lower_bound > upper_bound:
        return no_update, no_update, FAIL_BOUNDS_ELEMENT
    return lower_bound, upper_bound, ""


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
    return compounds_list, compounds_list[0]


activity_icons = {
    "active": html.I(className="fas fa-check-circle text-success"),
    True: html.I(className="fas fa-check-circle text-success"),
    "inactive": html.I(className="fas fa-times-circle text-danger"),
    False: html.I(className="fas fa-times-circle text-danger"),
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

    modulation_ic50 = four_param_logistic(
        entry["ic50"],
        entry["BOTTOM"],
        entry["TOP"],
        entry["ic50"],
        entry["slope"],
    )

    concentration_50 = find_argument_four_param_logistic(
        50,
        entry["BOTTOM"],
        entry["TOP"],
        entry["ic50"],
        entry["slope"],
    )

    smiles_row = pd.read_parquet("dashboard/assets/ml/predictions.pq").loc[
        lambda df: df["EOS"] == selected_compound
    ]
    smiles, toxicity = (
        smiles_row["smiles"].to_numpy()[0],
        smiles_row["toxicity"].to_numpy()[0],
    )
    smiles_graph = plot_smiles(smiles)
    smiles_html = dhtml.DangerouslySetInnerHTML(smiles_graph)

    if type(concentration_50) == complex:
        concentration_50 = "Not found"
    else:
        concentration_50 = f"{round(concentration_50, 5)} µM"

    result = {
        "min_modulation": round(entry["min_value"], 5),
        "max_modulation": round(entry["max_value"], 5),
        "ic50": round(entry["ic50"], 5),
        "modulation_ic50": round(modulation_ic50, 5),
        "concentration_50": concentration_50,
        "curve_slope": round(entry["slope"], 5),
        "r2": round(entry["r2"] * 100, 5),
        "is_active": html.Span(
            children=[
                activity_icons[entry["activity_final"]],
                html.Span(entry["activity_final"].upper(), className="ms-1"),
            ]
        ),
        "is_partially_active": html.Span(
            children=[
                activity_icons[entry["is_partially_active"]],
                html.Span(
                    "TRUE" if entry["is_partially_active"] else "FALSE",
                    className="ms-1",
                ),
            ]
        ),
        "graph": graph,
        "top": round(entry["TOP"], 5),
        "bottom": round(entry["BOTTOM"], 5),
        "smiles": smiles_html,
        "toxicity": round(float(toxicity), 5),
    }

    report_data = result.copy()
    report_data["html_graph"] = graph.to_html(full_html=False, include_plotlyjs="cdn")
    report_data["html_smiles_graph"] = smiles_graph
    report_data["is_active_html"] = entry["activity_final"]
    report_data["is_partially_active_html"] = entry["is_partially_active"]

    return list(result.values()) + [report_data]


def on_save_individual_EOS_result_button_click(n_clicks, report_data, eos):
    report_data["id"] = eos
    filename = f"{eos}_report_{datetime.now().strftime('%Y-%m-%d')}.html"
    jinja_template = generate_jinja_report(report_data)
    return dict(content=jinja_template, filename=filename)


# === STAGE 3 ===


def on_json_generate_button_click(
    n_clicks,
    concentration_lower_bound: float,
    concentration_upper_bound: float,
    top_lower_bound: float,
    top_upper_bound: float,
    file_storage: FileStorage,
):
    filename = f"hit_validation_settings_{datetime.now().strftime('%Y-%m-%d')}.json"
    json_object = json.dumps(
        {
            "concentration_lower_bound": concentration_lower_bound,
            "concentration_upper_bound": concentration_upper_bound,
            "top_lower_bound": top_lower_bound,
            "top_upper_bound": top_upper_bound,
        },
        indent=4,
    )
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
        State("top-lower-bound-store", "data"),
        State("top-upper-bound-store", "data"),
        prevent_initial_call="initial_duplicate",
    )(functools.partial(on_file_upload, file_storage=file_storage))

    callback(
        Output("concentration-lower-bound-store", "data"),
        Output("concentration-upper-bound-store", "data"),
        Output("concentration-parameters-message", "children"),
        Input("concentration-lower-bound-input", "value"),
        Input("concentration-upper-bound-input", "value"),
    )(on_bounds_change)
    callback(
        Output("top-lower-bound-store", "data"),
        Output("top-upper-bound-store", "data"),
        Output("top-parameters-message", "children"),
        Input("top-lower-bound-input", "value"),
        Input("top-upper-bound-input", "value"),
    )(on_bounds_change)

    callback(
        Output("hit-browser-compound-dropdown", "options"),
        Output("hit-browser-compound-dropdown", "value"),
        Input(elements["STAGES_STORE"], "data"),
        State("user-uuid", "data"),
    )(functools.partial(on_hit_browser_stage_entry, file_storage=file_storage))

    callback(
        Output("min-modulation-value", "children"),
        Output("max-modulation-value", "children"),
        Output("ic50-value", "children"),
        Output("ic50-y-value", "children"),
        Output("concentration-50", "children"),
        Output("curve-slope-value", "children"),
        Output("r2-value", "children"),
        Output("is-active-value", "children"),
        Output("is-partially-active-value", "children"),
        Output("hit-browser-plot", "figure"),
        Output("hit-browser-top", "value"),
        Output("hit-browser-bottom", "value"),
        Output("smiles", "children"),
        Output("toxicity", "children"),
        Output("report-data-hit-validation-hit-browser", "data"),
        Input("hit-browser-compound-dropdown", "value"),
        Input("hit-browser-unstack-button", "n_clicks"),
        Input("hit-browser-apply-button", "n_clicks"),
        State("hit-browser-top", "value"),
        State("hit-browser-bottom", "value"),
        State("user-uuid", "data"),
    )(functools.partial(on_selected_compound_changed, file_storage=file_storage))

    callback(
        Output("download-EOS-individual-report", "data"),
        Input("save-individual-EOS-result-button", "n_clicks"),
        State("report-data-hit-validation-hit-browser", "data"),
        State("hit-browser-compound-dropdown", "value"),
        prevent_initial_call=True,
    )(functools.partial(on_save_individual_EOS_result_button_click))

    callback(
        Output("download-json-settings-hit-validation", "data"),
        Input("generate-json-button", "n_clicks"),
        State("concentration-lower-bound-store", "data"),
        State("concentration-upper-bound-store", "data"),
        State("top-lower-bound-store", "data"),
        State("top-upper-bound-store", "data"),
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
