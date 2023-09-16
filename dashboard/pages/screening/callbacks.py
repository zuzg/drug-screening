import base64
import functools
import io
import uuid
from datetime import datetime

import numpy as np
import pandas as pd
import plotly.graph_objects as go
import pyarrow as pa
from dash import Input, Output, State, callback, callback_context, dcc, no_update, html
from datetime import datetime
from typing import List

from dashboard.data.bmg_plate import filter_low_quality_plates, parse_bmg_files
from dashboard.data.combine import (
    aggregate_well_plate_stats,
    combine_bmg_echo_data,
    reorder_bmg_echo_columns,
    split_compounds_controls,
)
from dashboard.data.file_preprocessing.echo_files_parser import EchoFilesParser
from dashboard.pages.components import make_file_list_component
from dashboard.storage import FileStorage
from dashboard.visualization.plots import (
    plot_activation_inhibition_zscore,
    plot_control_values,
    plot_row_col_means,
    plot_z_per_plate,
    visualize_multiple_plates,
)
from dashboard.pages.components import make_file_list_component
from dashboard.report.generate_jinja_report import generate_jinja_report

# === STAGE 1 ===


def upload_bmg_data(contents, names, last_modified, stored_uuid, file_storage):
    if contents is None:
        return no_update

    if not stored_uuid:
        stored_uuid = str(uuid.uuid4())

    bmg_files = []
    callback_context.response

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
        file_storage.save_file(f"{stored_uuid}_bmg_df.pq", bmg_df.to_parquet())

    return (
        make_file_list_component(names, [], 2),
        stored_uuid,
    )


# === STAGE 2 ===

DISPLAYED_PLATES = 12
N_ROWS = 4
N_COLS = DISPLAYED_PLATES // N_ROWS


def on_heatmap_controls_clicked(
    n_clicks_prev: int,
    n_clicks_next: int,
    n_clicks_first: int,
    n_clicks_last: int,
    current_index: int,
    max_index: int,
) -> int:
    """
    Callback for heatmap pagination controls.
    Updates the index of the first plate to be displayed.

    :param n_clicks_prev: previous button click count
    :param n_clicks_next: next button click count
    :param n_clicks_first: first button click count
    :param n_clicks_last: last button click count
    :param current_index: current index of the first plate to be displayed
    :param max_index: maximum index of the first plate to be displayed
    :return: new index of the first plate to be displayed
    """
    triggered = callback_context.triggered[0]["prop_id"].split(".")[0]

    going_backwards = triggered == "heatmap-previous-btn"
    going_forwards = triggered == "heatmap-next-btn"
    going_first = triggered == "heatmap-first-btn"
    going_last = triggered == "heatmap-last-btn"

    if going_first:
        return 0

    if going_last:
        return max_index

    if going_backwards:
        if current_index - DISPLAYED_PLATES > max_index:
            return 0
        return max(0, current_index - DISPLAYED_PLATES)

    if going_forwards and current_index < max_index:
        return current_index + DISPLAYED_PLATES
    return no_update


def on_outlier_purge_stage_entry(
    current_stage: int,
    heatmap_start_index: int,
    outliers_only_checklist: list[str] | None,
    stored_uuid: str,
    file_storage: FileStorage,
) -> tuple[dict, go.Figure, int, str, int, int, int]:
    """
    Callback for the stage 2 entry.
    Loads the data from the storage and prepares the visualization.

    :param current_stage: current stage index of the process
    :param heatmap_start_index: index of the first plate to be displayed
    :param outliers_only_checklist: list selected values in the outliers only checklist
    :param stored_uuid: uuid of the stored data
    :param file_storage: storage object
    :return: heatmap plot, max index, index numerator text, plates count, compounds count, outliers count
    """
    show_only_with_outliers = bool(outliers_only_checklist)
    if current_stage != 1:
        return no_update

    raw_bmg = file_storage.read_file(f"{stored_uuid}_bmg_df.pq")
    bmg_df = pd.read_parquet(pa.BufferReader(raw_bmg))
    raw_vals = file_storage.read_file(f"{stored_uuid}_bmg_val.npz")
    bmg_vals = np.load(io.BytesIO(raw_vals))["arr_0"]

    plates_count = bmg_vals.shape[0]
    compounds_count = plates_count * bmg_vals.shape[2] * (bmg_vals.shape[3] - 2)
    outliers_count = (bmg_vals[:, 1] == 1).sum()

    report_data = {
        "plates_count": plates_count,
        "compounds_count": compounds_count,
        "outliers_count": outliers_count,
    }

    if show_only_with_outliers:
        has_outliers_mask = np.any(bmg_vals[:, 1] == 1, axis=(-1, -2))
        bmg_df = bmg_df[has_outliers_mask]
        bmg_vals = bmg_vals[has_outliers_mask]

    filtered_plates_count = bmg_vals.shape[0]

    vis_bmg_df = bmg_df.iloc[
        heatmap_start_index : heatmap_start_index + DISPLAYED_PLATES, :
    ]
    vis_bmg_vals = bmg_vals[
        heatmap_start_index : heatmap_start_index + DISPLAYED_PLATES
    ]

    fig = visualize_multiple_plates(vis_bmg_df, vis_bmg_vals, N_ROWS, N_COLS)
    index_text = f"{heatmap_start_index + 1} - {heatmap_start_index + DISPLAYED_PLATES} / {bmg_vals.shape[0]}"

    final_vis_df = (
        vis_bmg_df.set_index("barcode").applymap(lambda x: f"{x:.3f}").reset_index()
    )

    max_index = filtered_plates_count - filtered_plates_count % DISPLAYED_PLATES

    return (
        report_data,
        fig,
        max_index,
        index_text,
        plates_count,
        compounds_count,
        outliers_count,
        final_vis_df.to_dict("records"),
    )


# === STAGE 3 ===


def on_plates_stats_stage_entry(
    current_stage: int, value: float, stored_uuid: str, file_storage: FileStorage
) -> tuple[go.Figure, go.Figure, go.Figure, str, str]:
    """
    Callback for the stage 3 entry
    Loads the data from storage and prepares visualizations, depending on the
    Z threshold = slider value

    :param current_stage: current stage index of the process
    :param value: z threshold, slider value
    :param stored_uuid: uuid of the stored data
    :param file_storage: storage object
    :return: control values plot, mean row col plot, z values plot, selected threshold,
    number of deleted plates
    """
    if current_stage != 2:
        return no_update
    raw_bmg = file_storage.read_file(f"{stored_uuid}_bmg_df.pq")
    bmg_df = pd.read_parquet(pa.BufferReader(raw_bmg))
    raw_vals = file_storage.read_file(f"{stored_uuid}_bmg_val.npz")
    bmg_vals = np.load(io.BytesIO(raw_vals))["arr_0"]

    filtered_df, filtered_vals = filter_low_quality_plates(bmg_df, bmg_vals, value)
    num_removed = bmg_df.shape[0] - filtered_df.shape[0]

    control_values_fig = plot_control_values(filtered_df)
    row_col_fig = plot_row_col_means(filtered_vals)
    z_fig = plot_z_per_plate(filtered_df.barcode, filtered_df.z_factor)

    report_data = {
        "control_values_fig": control_values_fig.to_html(
            full_html=False, include_plotlyjs="cdn"
        )
    }
    return (
        control_values_fig,
        row_col_fig,
        z_fig,
        f"Number of deleted plates: {num_removed}",
        report_data,
    )


# === STAGE 4 ===


def upload_echo_data(
    contents, names, last_modified, eos_contents, stored_uuid, file_storage
):
    if contents is None or eos_contents is None:
        return no_update

    eos_decoded = base64.b64decode(eos_contents.split(",")[1]).decode("utf-8")
    eos_df = pd.read_csv(io.StringIO(eos_decoded), dtype="str")

    echo_files = []
    for content, filename in zip(contents, names):
        name, extension = filename.split(".")
        if extension == "csv":
            decoded = base64.b64decode(content.split(",")[1]).decode("utf-8")
            echo_files.append((filename, io.StringIO(decoded)))

    if echo_files:
        echo_parser = EchoFilesParser()
        echo_parser.parse_files(tuple(echo_files))
        no_eos_num = echo_parser.merge_eos(eos_df)
        echo_parser.retain_key_columns()
        echo_df = echo_parser.get_processed_echo_df()
        exceptions_df = echo_parser.get_processed_exception_df()
        file_storage.save_file(f"{stored_uuid}_echo_df.pq", echo_df.to_parquet())
        file_storage.save_file(
            f"{stored_uuid}_exceptions_df.pq", exceptions_df.to_parquet()
        )

    return make_file_list_component(
        names, [f"There are {no_eos_num} rows without EOS - skipping."], 1
    )


# === STAGE 5 ===


def on_summary_entry(
    current_stage: int, stored_uuid: str, file_storage: FileStorage
) -> tuple[pd.DataFrame, go.Figure, go.Figure, go.Figure]:
    """
    Callback for the stage 5 entry
    Loads the data from storage and prepares visualizations

    :param current_stage: current stage index of the process
    :param stored_uuid: uuid of the stored data
    :param file_storage: storage object
    :return: combined echo dataframe, control values plot, mean row col plot, z values plot
    """
    if current_stage != 4:
        return no_update
    echo_df = pd.read_parquet(
        pa.BufferReader(file_storage.read_file(f"{stored_uuid}_echo_df.pq"))
    )
    bmg_df = pd.read_parquet(
        pa.BufferReader(file_storage.read_file(f"{stored_uuid}_bmg_df.pq"))
    )
    bmg_vals = np.load(
        io.BytesIO(file_storage.read_file(f"{stored_uuid}_bmg_val.npz"))
    )["arr_0"]

    echo_bmg_combined = combine_bmg_echo_data(echo_df, bmg_df, bmg_vals, None)
    drop_duplicates = (
        True  # TODO: inform the user about it/allow for deciding what to do
    )

    if drop_duplicates:
        echo_bmg_combined = echo_bmg_combined.drop_duplicates()

    compounds_df, control_pos_df, control_neg_df = split_compounds_controls(
        echo_bmg_combined
    )

    z_score_min = round(compounds_df["Z-SCORE"].min())
    z_score_max = round(compounds_df["Z-SCORE"].max())
    activation_min = round(compounds_df["% ACTIVATION"].min())
    activation_max = round(compounds_df["% ACTIVATION"].max())
    inhibition_min = round(compounds_df["% INHIBITION"].min())
    inhibition_max = round(compounds_df["% INHIBITION"].max())

    file_storage.save_file(
        f"{stored_uuid}_echo_bmg_combined_df.pq", echo_bmg_combined.to_parquet()
    )

    cmpd_plate_stats_df = aggregate_well_plate_stats(compounds_df, assign_x_coords=True)
    pos_plate_stats_df = aggregate_well_plate_stats(control_pos_df)
    neg_plate_stats_df = aggregate_well_plate_stats(control_neg_df)
    plate_stats_dfs = [cmpd_plate_stats_df, pos_plate_stats_df, neg_plate_stats_df]

    file_storage.save_file(
        f"{stored_uuid}_plate_stats_df.pq", cmpd_plate_stats_df.to_parquet()
    )

    fig_z_score = plot_activation_inhibition_zscore(
        echo_bmg_combined,
        plate_stats_dfs,
        "Z-SCORE",
        (z_score_min, z_score_max),
    )

    fig_activation = plot_activation_inhibition_zscore(
        echo_bmg_combined,
        plate_stats_dfs,
        "% ACTIVATION",
        (activation_min, activation_max),
    )

    fig_inhibition = plot_activation_inhibition_zscore(
        echo_bmg_combined,
        plate_stats_dfs,
        "% INHIBITION",
        (inhibition_min, inhibition_max),
    )

    return (
        echo_bmg_combined.to_dict("records"),
        fig_z_score,
        fig_activation,
        fig_inhibition,
        z_score_min,
        z_score_max,
        activation_min,
        activation_max,
        inhibition_min,
        inhibition_max,
    )


def on_filter_radio_or_range_update(
    key: str,
    z_score_min: float,
    z_score_max: float,
    activation_min: float,
    activation_max: float,
    inhibition_min: float,
    inhibition_max: float,
) -> dict:
    """
    Callback for the filter radio button update

    :param key: key to filter by
    :param z_score_min: min z-score value
    :param z_score_max: max z-score value
    :param activation_min: min activation value
    :param activation_max: max activation value
    :param inhibition_min: min inhibition value
    :param inhibition_max: max inhibition value
    :return: dictionary storing the ranges of interest
    """

    report_data_csv = {"key": key}

    if key == "z_score":
        report_data_csv["key_min"] = z_score_min
        report_data_csv["key_max"] = z_score_max
    elif key == "activation":
        report_data_csv["key_min"] = activation_min
        report_data_csv["key_max"] = activation_max
    elif key == "inhibition":
        report_data_csv["key_min"] = inhibition_min
        report_data_csv["key_max"] = inhibition_max

    return report_data_csv


def on_range_update(
    min_value: float, max_value: float, figure: go.Figure, key: str
) -> go.Figure:
    """
    Callback for the z-score range update button
    Adds the range to the plot

    :param min_value: min value of the range
    :param max_value: max value of the range
    :param figure: figure to update
    :return: updated figure
    """

    if max_value is None or max_value is None or max_value < min_value:
        return figure, True

    new_figure = go.Figure(figure)
    trace_name = "MIN/MAX range"
    trace_data = next(filter(lambda trace: trace.name == trace_name, new_figure.data))

    new_figure.update_traces(
        y=[min_value for y in trace_data.y],
        hovertemplate=f"{key} min.: {min_value}<extra></extra>",
        selector=dict(name=trace_name),
    )

    new_figure.update_traces(
        y=[max_value for y in trace_data.y],
        hovertemplate=f"{key} max.: {max_value}<extra></extra>",
        selector=dict(name="max"),
    )

    return new_figure, False


def on_apply_button_click(
    n_clicks: int,
    stored_uuid: str,
    min_value: float,
    max_value: float,
    figure: go.Figure,
    file_storage: FileStorage,
    key: str = "Z-SCORE",
) -> tuple[go.Figure, dict]:
    new_figure = go.Figure(figure)

    PLATE = "Destination Plate Barcode"
    WELL = "Destination Well"

    echo_bmg_combined_df = pd.read_parquet(
        pa.BufferReader(
            file_storage.read_file(f"{stored_uuid}_echo_bmg_combined_df.pq")
        )
    )

    compounds_df, _, _ = split_compounds_controls(echo_bmg_combined_df)
    cmpd_stats_df = pd.read_parquet(
        pa.BufferReader(file_storage.read_file(f"{stored_uuid}_plate_stats_df.pq"))
    )

    mask = (compounds_df[key] >= min_value) & (compounds_df[key] <= max_value)
    outside_range_df = compounds_df[~mask].copy()
    outside_range_df = outside_range_df[[key, WELL, PLATE]].merge(
        cmpd_stats_df[[f"{key}_x", PLATE]], on=PLATE
    )

    new_figure.update_traces(
        x=outside_range_df[f"{key}_x"],
        y=outside_range_df[key],
        customdata=np.stack((outside_range_df[PLATE], outside_range_df[WELL]), axis=-1),
        selector=dict(name="COMPOUNDS OUTSIDE"),
    )

    return new_figure


# === STAGE 6 ===


def on_save_results_click(
    n_clicks: int,
    stored_uuid: str,
    report_data_csv: dict,
    file_storage: FileStorage,
) -> None:
    """
    Callback for the save results button

    :param n_clicks: number of clicks
    :param stored_uuid: uuid of the stored data
    :param report_data_csv: dictionary storing the filter and ranges of interest
    :param file_storage: storage object
    :return: None
    """

    filename = f"screening_results_{datetime.now().strftime('%Y-%m-%d')}.csv"

    echo_bmg_combined_df = pd.read_parquet(
        pa.BufferReader(
            file_storage.read_file(f"{stored_uuid}_echo_bmg_combined_df.pq")
        ),
    )

    if report_data_csv["key"] == "z_score":
        mask = (echo_bmg_combined_df["Z-SCORE"] <= report_data_csv["key_min"]) | (
            echo_bmg_combined_df["Z-SCORE"] >= report_data_csv["key_max"]
        )
        echo_bmg_combined_df = echo_bmg_combined_df[mask]
    elif report_data_csv["key"] == "activation":
        mask = (echo_bmg_combined_df["% ACTIVATION"] <= report_data_csv["key_min"]) | (
            echo_bmg_combined_df["% ACTIVATION"] >= report_data_csv["key_max"]
        )
        echo_bmg_combined_df = echo_bmg_combined_df[mask]
    elif report_data_csv["key"] == "inhibition":
        mask = (echo_bmg_combined_df["% INHIBITION"] <= report_data_csv["key_min"]) | (
            echo_bmg_combined_df["% INHIBITION"] >= report_data_csv["key_max"]
        )
        echo_bmg_combined_df = echo_bmg_combined_df[mask]

    return dcc.send_data_frame(echo_bmg_combined_df.to_csv, filename)


def on_report_generate_button_click(
    n_clicks,
    stored_uuid: str,
    report_data_second_stage: dict,
    report_data_third_stage: dict,
    file_storage: FileStorage,
):
    filename = f"screening_report_{datetime.now().strftime('%Y-%m-%d')}.html"
    report_data_second_stage.update(report_data_third_stage)
    jinja_template = generate_jinja_report(report_data_second_stage)
    return html.Div(
        className="col",
        children=[
            html.H5(
                className="text-center",
                children=f"Report generated",
            ),
        ],
    ), dict(content=jinja_template, filename=filename)


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
        Input("heatmap-first-btn", "n_clicks"),
        Input("heatmap-last-btn", "n_clicks"),
        State("heatmap-start-index", "data"),
        State("max-heatmap-index", "data"),
    )(on_heatmap_controls_clicked)

    callback(
        Output("report-data-second-stage", "data"),
        Output("plates-heatmap-graph", "figure"),
        Output("max-heatmap-index", "data"),
        Output("heatmap-index-display", "children"),
        Output("total-plates", "children"),
        Output("total-compounds", "children"),
        Output("total-outliers", "children"),
        Output("plates-table", "data"),
        Input(elements["STAGES_STORE"], "data"),
        Input("heatmap-start-index", "data"),
        Input("heatmap-outliers-checklist", "value"),
        State("user-uuid", "data"),
    )(functools.partial(on_outlier_purge_stage_entry, file_storage=file_storage))

    callback(
        Output("control-values", "figure"),
        Output("mean-cols-rows", "figure"),
        Output("z-per-plate", "figure"),
        Output("plates-removed", "children"),
        Output("report-data-third-stage", "data"),
        Input(elements["STAGES_STORE"], "data"),
        Input("z-slider", "value"),
        State("user-uuid", "data"),
    )(functools.partial(on_plates_stats_stage_entry, file_storage=file_storage))

    callback(
        Output("echo-filenames", "children"),
        Input("upload-echo-data", "contents"),
        Input("upload-echo-data", "filename"),
        Input("upload-echo-data", "last_modified"),
        Input("upload-eos-mapping", "contents"),
        State("user-uuid", "data"),
    )(functools.partial(upload_echo_data, file_storage=file_storage))

    callback(
        Output("echo-bmg-combined", "data"),
        Output("z-score-plot", "figure"),
        Output("activation-plot", "figure"),
        Output("inhibition-plot", "figure"),
        Output("z-score-min-input", "value"),
        Output("z-score-max-input", "value"),
        Output("activation-min-input", "value"),
        Output("activation-max-input", "value"),
        Output("inhibition-min-input", "value"),
        Output("inhibition-max-input", "value"),
        Input(elements["STAGES_STORE"], "data"),
        State("user-uuid", "data"),
    )(functools.partial(on_summary_entry, file_storage=file_storage))

    callback(
        Output("z-score-plot", "figure", allow_duplicate=True),
        Output("z-score-button", "disabled"),
        Input("z-score-min-input", "value"),
        Input("z-score-max-input", "value"),
        State("z-score-plot", "figure"),
        prevent_initial_call=True,
    )(functools.partial(on_range_update, key="Z-SCORE"))
    callback(
        Output("z-score-plot", "figure", allow_duplicate=True),
        Input("z-score-button", "n_clicks"),
        State("user-uuid", "data"),
        State("z-score-min-input", "value"),
        State("z-score-max-input", "value"),
        State("z-score-plot", "figure"),
        prevent_initial_call=True,
    )(
        functools.partial(
            on_apply_button_click, file_storage=file_storage, key="Z-SCORE"
        )
    )
    callback(
        Output("activation-plot", "figure", allow_duplicate=True),
        Output("activation-button", "disabled"),
        Input("activation-min-input", "value"),
        Input("activation-max-input", "value"),
        State("activation-plot", "figure"),
        prevent_initial_call=True,
    )(functools.partial(on_range_update, key="% ACTIVATION"))
    callback(
        Output("activation-plot", "figure", allow_duplicate=True),
        Input("activation-button", "n_clicks"),
        State("user-uuid", "data"),
        State("activation-min-input", "value"),
        State("activation-max-input", "value"),
        State("activation-plot", "figure"),
        prevent_initial_call=True,
    )(
        functools.partial(
            on_apply_button_click, file_storage=file_storage, key="% ACTIVATION"
        )
    )
    callback(
        Output("inhibition-plot", "figure", allow_duplicate=True),
        Output("inhibition-button", "disabled"),
        Input("inhibition-min-input", "value"),
        Input("inhibition-max-input", "value"),
        State("inhibition-plot", "figure"),
        prevent_initial_call=True,
    )(functools.partial(on_range_update, key="% INHIBITION"))
    callback(
        Output("inhibition-plot", "figure", allow_duplicate=True),
        Input("inhibition-button", "n_clicks"),
        State("user-uuid", "data"),
        State("inhibition-min-input", "value"),
        State("inhibition-max-input", "value"),
        State("inhibition-plot", "figure"),
        prevent_initial_call=True,
    )(
        functools.partial(
            on_apply_button_click, file_storage=file_storage, key="% INHIBITION"
        )
    )
    callback(
        Output("report-data-csv", "data"),
        Input("filter-radio", "value"),
        Input("z-score-min-input", "value"),
        Input("z-score-max-input", "value"),
        Input("activation-min-input", "value"),
        Input("activation-max-input", "value"),
        Input("inhibition-min-input", "value"),
        Input("inhibition-max-input", "value"),
    )(functools.partial(on_filter_radio_or_range_update))
    callback(
        Output("download-echo-bmg-combined", "data"),
        Input("save-results-button", "n_clicks"),
        State("user-uuid", "data"),
        State("report-data-csv", "data"),
        prevent_initial_call=True,
    )(functools.partial(on_save_results_click, file_storage=file_storage))

    callback(
        Output("report_callback_receiver", "children"),
        Output("download-html-raport", "data"),
        Input("generate-report-button", "n_clicks"),
        State("user-uuid", "data"),
        State("report-data-second-stage", "data"),
        State("report-data-third-stage", "data"),
        prevent_initial_call=True,
    )(functools.partial(on_report_generate_button_click, file_storage=file_storage))
