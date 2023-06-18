import base64
import functools
import io
import uuid
from math import ceil, floor

import numpy as np
import pandas as pd
import plotly.graph_objects as go
import pyarrow as pa
import pyarrow.parquet as pq
from dash import Input, Output, State, callback, callback_context, dcc, html, no_update

from dashboard.data.bmg_plate import filter_low_quality_plates, parse_bmg_files
from dashboard.data.combine import combine_bmg_echo_data, split_compounds_controls
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
from dashboard.visualization.z_score_plot import plot_zscore

# === STAGE 1 ===


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
    return (
        control_values_fig,
        row_col_fig,
        z_fig,
        f"Number of deleted plates: {num_removed}",
    )


# === STAGE 4 ===


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

    return make_file_list_component(names, [], 1)


# === STAGE 5 ===


def on_summary_entry(current_stage: int, stored_uuid: str, file_storage: FileStorage):
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

    echo_bmg_combined = combine_bmg_echo_data(echo_df, bmg_df, bmg_vals, None)
    compounds_df, control_pos_df, control_neg_df = split_compounds_controls(
        echo_bmg_combined
    )

    echo_bmg_combined = (
        echo_bmg_combined.drop_duplicates()
    )  # TODO: inform the user about it/allow for deciding what to do

    print(echo_bmg_combined.head())
    echo_bmg_combined = echo_bmg_combined.reset_index().to_dict("records")

    # NOTE: check the range of the z-score that's needed
    min_z, max_z = compounds_df["Z-SCORE"].min(), compounds_df["Z-SCORE"].max()
    marks = {i: "{}".format(i) for i in range(0, ceil(max_z), 5)}
    if floor(min_z) < 0:
        marks.update({i: "{}".format(i) for i in range(floor(min_z), 0, 5)})

    # NOTE: here I only added the position that is required for the plot_zscore function
    if "id_pos" not in compounds_df.columns:
        fig_z_score, new_echo_df = plot_zscore(
            compounds_df, control_pos_df, control_neg_df
        )
        serialized_new_echo_df = new_echo_df.reset_index().to_parquet()
        file_storage.save_file(f"{stored_uuid}_echo_df.pq", serialized_new_echo_df)
    else:
        fig_z_score, _ = plot_zscore(compounds_df, control_pos_df, control_neg_df)

    z_score_slider = dcc.RangeSlider(
        floor(min_z),
        ceil(max_z),
        value=[min_z, max_z],
        tooltip={
            "placement": "bottom",
            "always_visible": True,
        },
        marks=marks,
        allowCross=False,
        id="z-score-slider",
    )

    fig_activation = visualize_activation_inhibition_zscore(
        compounds_df, control_pos_df, control_neg_df, "% ACTIVATION"
    )

    fig_inhibition = visualize_activation_inhibition_zscore(
        compounds_df, control_pos_df, control_neg_df, "% INHIBITION"
    )

    return (
        echo_bmg_combined,
        fig_z_score,
        fig_activation,
        fig_inhibition,
        z_score_slider,
    )


def on_z_score_range_update(value, figure):
    min_value, max_value = value
    new_figure = go.Figure(figure)

    shapes = []
    annotations = []

    shapes.append(
        {
            "type": "line",
            "y0": min_value,
            "y1": min_value,
            "line": {
                "color": "red",
                "width": 3,
                "dash": "dash",
            },
        }
    )

    shapes.append(
        {
            "type": "line",
            "y0": max_value,
            "y1": max_value,
            "line": {
                "color": "red",
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
            "font": {"color": "red"},
        }
    )

    annotations.append(
        {
            # "x": 10,
            # "xanchor": "right",
            "y": max_value,
            "text": f"MAX: {max_value:.2f}",
            "showarrow": False,
            "font": {"color": "red"},
        }
    )

    new_figure.update_layout(shapes=shapes, annotations=annotations)
    return new_figure, False


def on_z_score_button_click(
    n_clicks, stored_uuid, value, figure, file_storage: FileStorage
):
    min_value, max_value = value
    new_figure = go.Figure(figure)
    selector = dict(name="COMPOUNDS OUTSIDE")

    id_pos = "id_pos"
    PLATE = "Destination Plate Barcode"
    WELL = "Destination Well"
    Z_SCORE = "Z-SCORE"

    echo_df = pd.read_parquet(
        pa.BufferReader(file_storage.read_file(f"{stored_uuid}_echo_df.pq"))
    )

    # TBD: use pa.ParquetDataset
    compounds_outside_df = echo_df[
        (echo_df[id_pos].notnull())
        & ((echo_df[Z_SCORE] < min_value) | (echo_df[Z_SCORE] > max_value))
    ][[id_pos, PLATE, WELL, Z_SCORE]]

    new_figure.update_traces(
        x=compounds_outside_df[id_pos],
        y=compounds_outside_df[Z_SCORE],
        customdata=np.stack(
            (compounds_outside_df[PLATE], compounds_outside_df[WELL]), axis=-1
        ),
        hovertemplate="plate: %{customdata[0]}<br>well: %{customdata[1]}<br>z-score: %{y:.2f}<extra>CMPD ID</extra>",
        mode="markers",
        selector=selector,
    )
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
        Output("heatmap-start-index", "data"),
        Input("heatmap-previous-btn", "n_clicks"),
        Input("heatmap-next-btn", "n_clicks"),
        Input("heatmap-first-btn", "n_clicks"),
        Input("heatmap-last-btn", "n_clicks"),
        State("heatmap-start-index", "data"),
        State("max-heatmap-index", "data"),
    )(on_heatmap_controls_clicked)

    callback(
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
        Input(elements["STAGES_STORE"], "data"),
        Input("z-slider", "value"),
        State("user-uuid", "data"),
    )(functools.partial(on_plates_stats_stage_entry, file_storage=file_storage))
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
        Output("z-score-slider", "children"),
        Input(elements["STAGES_STORE"], "data"),
        State("user-uuid", "data"),
    )(functools.partial(on_summary_entry, file_storage=file_storage))
    callback(
        Output("z-score-plot", "figure", allow_duplicate=True),
        Output("z-score-button", "disabled"),
        Input("z-score-slider", "value"),
        State("z-score-plot", "figure"),
        prevent_initial_call=True,
    )(functools.partial(on_z_score_range_update))
    callback(
        Output("z-score-plot", "figure", allow_duplicate=True),
        Input("z-score-button", "n_clicks"),
        State("user-uuid", "data"),
        State("z-score-slider", "value"),
        State("z-score-plot", "figure"),
        prevent_initial_call=True,
    )(functools.partial(on_z_score_button_click, file_storage=file_storage))
