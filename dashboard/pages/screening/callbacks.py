import base64
import functools
import io
import json
import uuid
from datetime import datetime

import numpy as np
import pandas as pd
import plotly.graph_objects as go
import pyarrow as pa
from dash import (
    Input,
    Output,
    State,
    callback,
    callback_context,
    dash_table,
    dcc,
    html,
    no_update,
)

from dashboard.data.bmg_plate import filter_low_quality_plates, parse_bmg_files
from dashboard.data.combine import (
    aggregate_well_plate_stats,
    combine_bmg_echo_data,
    split_compounds_controls,
)
from dashboard.data.file_preprocessing.echo_files_parser import EchoFilesParser
from dashboard.data.utils import eos_to_ecbd_link
from dashboard.pages.components import make_file_list_component
from dashboard.pages.screening.report.generate_jinja_report import generate_jinja_report
from dashboard.pages.screening.report.generate_json_data import read_stages_stats
from dashboard.storage import FileStorage
from dashboard.visualization.plots import (
    plot_activation_inhibition_zscore,
    plot_control_values,
    plot_row_col_means,
    plot_z_per_plate,
    visualize_multiple_plates,
)
from dashboard.visualization.text_tables import (
    make_filter_radio_options,
    make_summary_stage_datatable,
)


def on_next_button_click(n_clicks):
    return True


# === STAGE 1 ===


def upload_bmg_data(contents, names, last_modified, stored_uuid, file_storage):
    if contents is None:
        return no_update, no_update, no_update, no_update

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
        no_update,
        stored_uuid,
        False,
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

    report_data = {
        "plates_count": plates_count,
        "compounds_count": compounds_count,
        "outliers_count": outliers_count,
        "outliers_only_checklist": show_only_with_outliers,
    }

    return (
        report_data,
        fig,
        max_index,
        index_text,
        plates_count,
        compounds_count,
        outliers_count,
        final_vis_df.to_dict("records"),
        False,
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
        ),
        "z_slider_value": value,
        "row_col_fig": row_col_fig.to_html(full_html=False, include_plotlyjs="cdn"),
        "z_fig": z_fig.to_html(full_html=False, include_plotlyjs="cdn"),
    }

    z_slider_data = {"z_slider_value": value}

    return (
        control_values_fig,
        row_col_fig,
        z_fig,
        f"Number of deleted plates: {num_removed}/{bmg_df.shape[0]}",
        report_data,
        z_slider_data,
        False,
    )


# === STAGE 4 ===


def on_upload_echo_data(contents, names, last_modified, stored_uuid, file_storage):
    if contents is None:
        return no_update

    echo_files = []
    for content, filename in zip(contents, names):
        name, extension = filename.split(".")
        if extension == "csv":
            decoded = base64.b64decode(content.split(",")[1]).decode("utf-8")
            echo_files.append((filename, io.StringIO(decoded)))

    if echo_files:
        echo_parser = EchoFilesParser()
        echo_parser.parse_files(tuple(echo_files))
        echo_parser.retain_key_columns(eos=False, exceptions=True)
        echo_df = echo_parser.get_processed_echo_df()
        exceptions_df = echo_parser.get_processed_exception_df()
        file_storage.save_file(f"{stored_uuid}_echo_df.pq", echo_df.to_parquet())
        file_storage.save_file(
            f"{stored_uuid}_exceptions_df.pq", exceptions_df.to_parquet()
        )

    return None  # dummy upload echo return


def on_upload_eos_data(contents, stored_uuid, file_storage):
    if contents is None:
        return no_update

    eos_decoded = base64.b64decode(contents.split(",")[1]).decode("utf-8")
    eos_df = pd.read_csv(io.StringIO(eos_decoded), dtype="str")
    file_storage.save_file(f"{stored_uuid}_eos_df.pq", eos_df.to_parquet())
    return None  # dummy upload eos return


def on_upload_echo_eos_data(echo_upload, names, eos_upload, stored_uuid, file_storage):
    echo_df_file_path = f"{stored_uuid}_echo_df.pq"
    eos_df_file_path = f"{stored_uuid}_eos_df.pq"

    if not file_storage.file_exists(echo_df_file_path) or not file_storage.file_exists(
        eos_df_file_path
    ):
        return no_update

    echo_df = pd.read_parquet(
        pa.BufferReader(file_storage.read_file(echo_df_file_path))
    )
    eos_df = pd.read_parquet(pa.BufferReader(file_storage.read_file(eos_df_file_path)))
    echo_parser = EchoFilesParser()
    echo_parser.set_echo_df(echo_df)
    echo_parser.retain_key_columns(eos=False)

    no_eos_num = echo_parser.merge_eos(eos_df)
    echo_df = echo_parser.retain_key_columns().get_processed_echo_df()
    file_storage.save_file(f"{stored_uuid}_echo_df.pq", echo_df.to_parquet())

    return (
        make_file_list_component(
            names, [f"There are {no_eos_num} rows without EOS - skipping."], 1
        ),
        False,
    )


def on_additional_options_change(
    key: str,
    formula: str,
) -> dict[str, str]:
    """
    Update the additional screening options dictionary

    :param screening_feature: screening feature
    :param formula: formula
    :return: updated dictionary
    """
    disabled = key != "activation"
    options_dict = {}
    options_dict["key"] = key
    options_dict["feature_column"] = "% " + key.upper()
    options_dict["without_pos"] = formula
    return options_dict, disabled


# === STAGE 5 ===


def on_summary_entry(
    current_stage: int,
    stored_uuid: str,
    z_slider: float,
    screening_options: dict,
    file_storage: FileStorage,
) -> tuple[
    pd.DataFrame, go.Figure, go.Figure, float, float, float, float, str, html.Div
]:
    """
    Callback for the stage 5 entry
    Loads the data from storage and prepares visualizations

    :param current_stage: current stage index of the process
    :param stored_uuid: uuid of the stored data
    :param z_slider: z threshold, slider value
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

    filtered_df, filtered_vals = filter_low_quality_plates(
        bmg_df, bmg_vals, z_slider["z_slider_value"]
    )

    echo_bmg_combined = combine_bmg_echo_data(
        echo_df,
        filtered_df,
        filtered_vals,
        screening_options["key"],
        screening_options["without_pos"],
    )
    echo_bmg_combined = echo_bmg_combined.drop_duplicates()

    compounds_df, control_pos_df, control_neg_df = split_compounds_controls(
        echo_bmg_combined
    )
    compounds_df = compounds_df.dropna()
    file_storage.save_file(
        f"{stored_uuid}_echo_bmg_combined_df.pq", compounds_df.to_parquet()
    )

    cmpd_plate_stats_df = aggregate_well_plate_stats(
        compounds_df, screening_options["feature_column"], assign_x_coords=True
    )
    pos_plate_stats_df = aggregate_well_plate_stats(
        control_pos_df, screening_options["feature_column"]
    )
    neg_plate_stats_df = aggregate_well_plate_stats(
        control_neg_df, screening_options["feature_column"]
    )
    plate_stats_dfs = [cmpd_plate_stats_df, pos_plate_stats_df, neg_plate_stats_df]

    file_storage.save_file(
        f"{stored_uuid}_plate_stats_df.pq", cmpd_plate_stats_df.to_parquet()
    )

    feature_min = round(compounds_df[screening_options["feature_column"]].min())
    feature_max = round(compounds_df[screening_options["feature_column"]].max())

    fig_z_score = plot_activation_inhibition_zscore(
        compounds_df,
        plate_stats_dfs,
        "Z-SCORE",
        (-3, 3),  # z-score min and max
    )

    fig_feature = plot_activation_inhibition_zscore(
        compounds_df,
        plate_stats_dfs,
        screening_options["feature_column"],
        (feature_min, feature_max),
    )

    compounds_url_df = eos_to_ecbd_link(compounds_df)
    summary_stage_datatable = make_summary_stage_datatable(
        compounds_url_df, screening_options["feature_column"]
    )

    radio_options = make_filter_radio_options(screening_options["key"])

    report_data = {
        "fig_z_score": fig_z_score.to_html(full_html=False, include_plotlyjs="cdn"),
        "fig_feature": fig_feature.to_html(full_html=False, include_plotlyjs="cdn"),
    }

    return (
        summary_stage_datatable,
        fig_z_score,
        fig_feature,
        -3,  # z_score_min,
        3,  # z_score_max,
        False,  # min input disabled
        False,  # max input disabled
        feature_min,
        feature_max,
        False,  # min input disabled
        False,  # max input disabled
        f"number of compounds: {len(compounds_df)}",
        f"{screening_options['feature_column']} range:",
        radio_options,
        report_data,
        False,  # next button disabled
    )


def on_filter_radio_or_range_update(
    key: str,
    z_score_min: float,
    z_score_max: float,
    feature_min: float,
    feature_max: float,
) -> dict:
    """
    Callback for the filter radio button update

    :param key: key to filter by
    :param z_score_min: min z-score value
    :param z_score_max: max z-score value
    :param feature_min: min feature value
    :param feature_max: max feature value
    :return: dictionary storing the ranges of interest
    """

    report_data_csv = {"key": key}

    if key == "z_score":
        report_data_csv["key_min"] = z_score_min
        report_data_csv["key_max"] = z_score_max
    elif key == "activation" or key == "inhibition":
        report_data_csv["key_min"] = feature_min
        report_data_csv["key_max"] = feature_max
    return report_data_csv


def on_range_update(
    min_value: float,
    max_value: float,
    figure: go.Figure,
    stored_uuid: str,
    key: dict,
    file_storage: FileStorage,
) -> go.Figure:
    """
    Callback for the z-score range update button
    Adds the range to the plot and updates the compounds outside range

    :param min_value: min value of the range
    :param max_value: max value of the range
    :param figure: figure to update
    :param stored_uuid: uuid of the stored data
    :param file_storage: storage object
    :param key: key to filter by
    :return: updated figure
    """
    if key != "Z-SCORE":
        key = key["feature_column"]

    if min_value is None or max_value is None or max_value < min_value:
        return figure

    new_figure = go.Figure(figure)

    # update the min/max range
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

    # update the compounds outside range
    PLATE = "Destination Plate Barcode"
    WELL = "Destination Well"

    compounds_df = pd.read_parquet(
        pa.BufferReader(
            file_storage.read_file(f"{stored_uuid}_echo_bmg_combined_df.pq")
        )
    )
    cmpd_stats_df = pd.read_parquet(
        pa.BufferReader(file_storage.read_file(f"{stored_uuid}_plate_stats_df.pq"))
    )

    mask = (compounds_df[key] >= min_value) & (compounds_df[key] <= max_value)
    outside_range_df = compounds_df[~mask].copy()
    outside_range_df = outside_range_df[[key, WELL, PLATE, "EOS"]].merge(
        cmpd_stats_df[[f"{key}_x", PLATE]], on=PLATE
    )

    new_figure.update_traces(
        x=outside_range_df[f"{key}_x"],
        y=outside_range_df[key],
        customdata=np.stack((outside_range_df[PLATE], outside_range_df[WELL]), axis=-1),
        text=outside_range_df["EOS"],
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

    echo_bmg_combined_df = echo_bmg_combined_df.reset_index(drop=True)

    return dcc.send_data_frame(echo_bmg_combined_df.to_csv, filename)


def on_save_exceptions_click(
    n_clicks: int,
    stored_uuid: str,
    file_storage: FileStorage,
) -> None:
    """
    Callback for the save exceptions button

    :param n_clicks: number of clicks
    :param stored_uuid: uuid of the stored data
    :param file_storage: storage object
    :return: None
    """

    filename = f"screening_exceptions_{datetime.now().strftime('%Y-%m-%d')}.csv"

    exceptions_df = pd.read_parquet(
        pa.BufferReader(file_storage.read_file(f"{stored_uuid}_exceptions_df.pq")),
    )

    return dcc.send_data_frame(exceptions_df.to_csv, filename)


def on_report_generate_button_click(
    n_clicks,
    report_data_second_stage: dict,
    report_data_third_stage: dict,
    report_data_screening_summary_plots: dict,
):
    filename = f"screening_report_{datetime.now().strftime('%Y-%m-%d')}.html"
    report_data_second_stage.update(report_data_third_stage)
    report_data_second_stage.update(report_data_screening_summary_plots)
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


def on_json_generate_button_click(
    n_clicks,
    report_data_second_stage: dict,
    report_data_third_stage: dict,
    report_data_csv: dict,
):
    filename = f"screening_settings_{datetime.now().strftime('%Y-%m-%d')}.json"
    process_settings = read_stages_stats(
        report_data_second_stage, report_data_third_stage, report_data_csv
    )
    json_object = json.dumps(process_settings, indent=4)
    return dict(content=json_object, filename=filename)


def register_callbacks(elements, file_storage):
    # callback(
    #     Output(elements["NEXT_BTN"], "disabled", allow_duplicate=True),
    #     Input(elements["NEXT_BTN"], "n_clicks"),
    #     prevent_initial_call=True,
    # )(on_next_button_click)
    callback(
        [
            Output("bmg-filenames", "children"),
            Output("dummy-upload-bmg-data", "children"),
            Output("user-uuid", "data"),
            Output({"type": elements["BLOCKER"], "index": 0}, "data"),
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
        Output({"type": elements["BLOCKER"], "index": 1}, "data"),
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
        Output("z-slider-value", "data"),
        Output({"type": elements["BLOCKER"], "index": 2}, "data"),
        Input(elements["STAGES_STORE"], "data"),
        Input("z-slider", "value"),
        State("user-uuid", "data"),
    )(functools.partial(on_plates_stats_stage_entry, file_storage=file_storage))

    callback(
        Output("dummy-upload-echo-data", "children"),
        Input("upload-echo-data", "contents"),
        Input("upload-echo-data", "filename"),
        Input("upload-echo-data", "last_modified"),
        State("user-uuid", "data"),
        prevent_initial_call=True,
    )(functools.partial(on_upload_echo_data, file_storage=file_storage))

    callback(
        Output("dummy-upload-eos-mapping", "children"),
        Input("upload-eos-mapping", "contents"),
        State("user-uuid", "data"),
        prevent_initial_call=True,
    )(functools.partial(on_upload_eos_data, file_storage=file_storage))

    callback(
        Output("echo-filenames", "children"),
        Output({"type": elements["BLOCKER"], "index": 3}, "data"),
        Input("dummy-upload-echo-data", "children"),
        Input("upload-echo-data", "filename"),
        Input("dummy-upload-eos-mapping", "children"),
        State("user-uuid", "data"),
        prevent_initial_call=True,
    )(functools.partial(on_upload_echo_eos_data, file_storage=file_storage))

    callback(
        Output("activation-inhibition-screening-options", "data"),
        Output("activation-formula-dropdown", "disabled"),
        Input("screening-feature-dropdown", "value"),
        Input("activation-formula-dropdown", "value"),
    )(on_additional_options_change)

    callback(
        Output("compounds-data-table", "children"),
        Output("z-score-plot", "figure"),
        Output("feature-plot", "figure"),
        Output("z-score-min-input", "value"),
        Output("z-score-max-input", "value"),
        Output("z-score-min-input", "disabled"),
        Output("z-score-max-input", "disabled"),
        Output("feature-min-input", "value"),
        Output("feature-max-input", "value"),
        Output("feature-min-input", "disabled"),
        Output("feature-max-input", "disabled"),
        Output("compounds-data-subtitle", "children"),
        Output("tab-feature-header", "children"),
        Output("filter-radio", "options"),
        Output("report-data-screening-summary-plots", "data"),
        Output({"type": elements["BLOCKER"], "index": 4}, "data"),
        Input(elements["STAGES_STORE"], "data"),
        State("user-uuid", "data"),
        State("z-slider-value", "data"),
        State("activation-inhibition-screening-options", "data"),
    )(functools.partial(on_summary_entry, file_storage=file_storage))
    # Z-SCORE
    callback(
        Output("z-score-plot", "figure", allow_duplicate=True),
        Input("z-score-min-input", "value"),
        Input("z-score-max-input", "value"),
        State("z-score-plot", "figure"),
        State("user-uuid", "data"),
        prevent_initial_call=True,
    )(functools.partial(on_range_update, key="Z-SCORE", file_storage=file_storage))
    # ACTIVATION/INHIBITION
    callback(
        Output("feature-plot", "figure", allow_duplicate=True),
        Input("feature-min-input", "value"),
        Input("feature-max-input", "value"),
        State("feature-plot", "figure"),
        State("user-uuid", "data"),
        State("activation-inhibition-screening-options", "data"),
        prevent_initial_call=True,
    )(functools.partial(on_range_update, file_storage=file_storage))
    callback(
        Output("report-data-csv", "data"),
        Input("filter-radio", "value"),
        Input("z-score-min-input", "value"),
        Input("z-score-max-input", "value"),
        Input("feature-min-input", "value"),
        Input("feature-max-input", "value"),
    )(on_filter_radio_or_range_update)
    callback(
        Output("download-echo-bmg-combined", "data"),
        Input("save-results-button", "n_clicks"),
        State("user-uuid", "data"),
        State("report-data-csv", "data"),
        prevent_initial_call=True,
    )(functools.partial(on_save_results_click, file_storage=file_storage))
    callback(
        Output("download-exceptions-csv", "data"),
        Input("save-exceptions-button", "n_clicks"),
        State("user-uuid", "data"),
        prevent_initial_call=True,
    )(functools.partial(on_save_exceptions_click, file_storage=file_storage))
    callback(
        Output("report_callback_receiver", "children"),
        Output("download-html-raport", "data"),
        Input("generate-report-button", "n_clicks"),
        State("report-data-second-stage", "data"),
        State("report-data-third-stage", "data"),
        State("report-data-screening-summary-plots", "data"),
        prevent_initial_call=True,
    )(on_report_generate_button_click)
    callback(
        Output("download-json-settings-screening", "data"),
        Input("generate-json-button", "n_clicks"),
        State("report-data-second-stage", "data"),
        State("report-data-third-stage", "data"),
        State("report-data-csv", "data"),
        prevent_initial_call=True,
    )(on_json_generate_button_click)
