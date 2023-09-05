import base64
import functools
import io
import uuid

import numpy as np
import pandas as pd
import plotly.graph_objects as go
import pyarrow as pa
from dash import Input, Output, State, callback, callback_context, dcc, no_update, html
from datetime import datetime
from typing import List

from dashboard.data.bmg_plate import filter_low_quality_plates, parse_bmg_files
from dashboard.data.combine import (
    combine_bmg_echo_data,
    reorder_bmg_echo_columns,
    split_compounds_controls,
)
from dashboard.data.file_preprocessing.echo_files_parser import EchoFilesParser
from dashboard.pages.components import make_file_list_component
from dashboard.storage import FileStorage
from dashboard.visualization.plots import (
    plot_control_values,
    plot_row_col_means,
    plot_z_per_plate,
    visualize_activation_inhibition_zscore,
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
        serialized_processed_df = bmg_df.reset_index().to_parquet()
        file_storage.save_file(f"{stored_uuid}_bmg_df.pq", serialized_processed_df)

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
) -> tuple[go.Figure, int, str, int, int, int]:
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
        vis_bmg_df.set_index("barcode")
        .drop(columns=["index"])
        .applymap(lambda x: f"{x:.3f}")
        .reset_index()
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
        echo_parser.merge_eos(eos_df)
        echo_parser.retain_key_columns()
        echo_df = echo_parser.get_processed_echo_df()
        exceptions_df = echo_parser.get_processed_exception_df()
        serialized_processed_df = echo_df.reset_index().to_parquet()
        file_storage.save_file(f"{stored_uuid}_echo_df.pq", serialized_processed_df)
        serialized_processed_exceptions_df = exceptions_df.reset_index().to_parquet()
        file_storage.save_file(
            f"{stored_uuid}_exceptions_df.pq", serialized_processed_exceptions_df
        )

    return make_file_list_component(names, [], 1)


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
    compounds_df, control_pos_df, control_neg_df = split_compounds_controls(
        echo_bmg_combined
    )

    echo_bmg_combined = (
        echo_bmg_combined.drop_duplicates()
    )  # TODO: inform the user about it/allow for deciding what to do
    echo_bmg_combined = echo_bmg_combined.reset_index()

    serialized_echo_bmg_combined = echo_bmg_combined.to_parquet()
    file_storage.save_file(
        f"{stored_uuid}_echo_bmg_combined_df.pq", serialized_echo_bmg_combined
    )

    fig_z_score = visualize_activation_inhibition_zscore(
        compounds_df, control_pos_df, control_neg_df, "Z-SCORE", (-3, 3)
    )

    fig_activation = visualize_activation_inhibition_zscore(
        compounds_df, control_pos_df, control_neg_df, "% ACTIVATION"
    )

    fig_inhibition = visualize_activation_inhibition_zscore(
        compounds_df, control_pos_df, control_neg_df, "% INHIBITION"
    )

    return (
        echo_bmg_combined.to_dict("records"),
        fig_z_score,
        fig_activation,
        fig_inhibition,
    )


def on_z_score_range_update(
    n_clicks: int, figure: go.Figure, range: tuple[float, float]
) -> go.Figure:
    """
    Callback for the z-score range update button
    Adds the range to the plot

    :param n_clicks: number of clicks
    :param figure: figure to update
    :param range: range to add
    :return: updated figure
    """
    min_value, max_value = range
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


# === STAGE 6 ===


def on_save_results_click(
    n_clicks: int, stored_uuid: str, file_storage: FileStorage
) -> None:
    """
    Callback for the save results button

    :param n_clicks: number of clicks
    :param stored_uuid: uuid of the stored data
    :param file_storage: storage object
    :return: None
    """

    filename = f"screening_results_{datetime.now().strftime('%Y-%m-%d')}.csv"

    echo_bmg_combined_df = pd.read_parquet(
        pa.BufferReader(
            file_storage.read_file(f"{stored_uuid}_echo_bmg_combined_df.pq")
        ),
    )

    echo_bmg_combined_df = reorder_bmg_echo_columns(echo_bmg_combined_df)
    return dcc.send_data_frame(echo_bmg_combined_df.to_csv, filename)


def on_report_generate_button_click(
    n_clicks,
    stored_uuid: str,
    report_data_second_stage: dict,
    report_data_third_stage: dict,
    file_storage: FileStorage,
):
    report_data_second_stage.update(report_data_third_stage)
    jinja_template = generate_jinja_report(report_data_second_stage)
    with open("report_primary_screening.html", "w") as f:
        f.write(jinja_template)
    return html.Div(
        className="col",
        children=[
            html.H5(
                className="text-center",
                children=f"Report generated",
            ),
        ],
    )


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
        Input(elements["STAGES_STORE"], "data"),
        State("user-uuid", "data"),
    )(functools.partial(on_summary_entry, file_storage=file_storage))

    callback(
        Output("z-score-plot", "figure", allow_duplicate=True),
        Input("z-score-button", "n_clicks"),
        State("z-score-plot", "figure"),
        State("z-score-slider", "value"),
        prevent_initial_call=True,
    )(functools.partial(on_z_score_range_update))

    callback(
        Output("download-echo-bmg-combined", "data"),
        Input("save-results-button", "n_clicks"),
        State("user-uuid", "data"),
        prevent_initial_call=True,
    )(functools.partial(on_save_results_click, file_storage=file_storage))

    callback(
        Output("report_callback_receiver", "children"),
        Input("generate-report-button", "n_clicks"),
        State("user-uuid", "data"),
        State("report-data-second-stage", "data"),
        State("report-data-third-stage", "data"),
    )(functools.partial(on_report_generate_button_click, file_storage=file_storage))
