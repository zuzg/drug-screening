import base64
import functools
import io
import uuid
from datetime import datetime
from typing import List, Tuple

import pandas as pd
import plotly.graph_objects as go
import pyarrow as pa
from dash import Input, Output, State, callback, dcc, html, no_update
from sklearn.decomposition import PCA
from umap import UMAP

from dashboard.data.controls import controls_index_annotator, generate_controls
from dashboard.data.preprocess import MergedAssaysPreprocessor
from dashboard.data.structural_similarity import prepare_cluster_viz
from dashboard.data.utils import eos_to_ecbd_link
from dashboard.pages.components import make_file_list_component
from dashboard.storage import FileStorage
from dashboard.visualization.plots import (
    make_projection_plot,
    plot_clustered_smiles,
    plot_projection_2d,
)
from dashboard.visualization.text_tables import pca_smiles_summary, table_from_df


def on_3d_checkbox_change(plot_3d: List[str]) -> bool:
    """
    Callback for the 3d checkbox change. Disables the download selection button if 3d is selected.


    :param plot_3d: 3d checkbox selection
    :return: boolean indicating if the button should be disabled
    """
    return bool(plot_3d)


# === STAGE 1 ===


def on_hit_validation_upload(
    contents: str, stored_uuid: str, file_storage: FileStorage
) -> Tuple[str, None]:
    """
    Callback for activity file upload.

    :param contents: base64 encoded file content
    :param stored_uuid: session uuid
    :param file_storage: file storage
    :return: session uuid, dummy activity upload return
    """
    if not stored_uuid:
        stored_uuid = str(uuid.uuid4())
    if contents is None:
        return no_update

    activity_decoded = base64.b64decode(contents.split(",")[1]).decode("utf-8")
    activity_df = pd.read_csv(io.StringIO(activity_decoded), dtype="str")
    file_storage.save_file(f"{stored_uuid}_activity_df.pq", activity_df.to_parquet())
    return stored_uuid, None  # dummy activity upload return


def on_smiles_files_upload(
    dummy_activity_upload: str,
    filename: str,
    smiles_content: str | None,
    smiles_filename: str,
    stored_uuid: str | None,
    file_storage: FileStorage,
) -> Tuple[html.Div, str]:
    """
    Callback for file upload.

    :param content: base64 encoded file content
    :param filename: file name
    :param last_modified: last modified timestamp
    :param smiles_content: base64 encoded smiles content
    :param stored_uuid: session uuid
    :param file_storage: file storage
    :return: list of loaded and not loaded files
    :return: next stage button disabled status
    """
    if not stored_uuid:
        stored_uuid = str(uuid.uuid4())

    activity_path = f"{stored_uuid}_activity_df.pq"

    if not file_storage.file_exists(activity_path) or not smiles_content:
        return no_update

    activity_df = pd.read_parquet(
        pa.BufferReader(file_storage.read_file(activity_path))
    )

    smiles_decoded = base64.b64decode(smiles_content.split(",")[1]).decode("utf-8")
    smiles_new = pd.read_csv(io.StringIO(smiles_decoded), dtype="str")
    smiles_active = pd.read_parquet("dashboard/assets/ml/predictions.pq")

    df_merged = prepare_cluster_viz(activity_df, smiles_active, smiles_new)

    saved_name = f"{stored_uuid}_smiles_merged.pq"
    file_storage.save_file(saved_name, df_merged.reset_index().to_parquet())

    return (
        html.Div(
            children=[
                make_file_list_component([filename, smiles_filename], [], 1),
            ],
        ),
        False,  # next stage button disabled status
        stored_uuid,
        None,  # dummy smiles upload return
    )


# === STAGE 2 ===


def on_plot_smiles(
    current_stage: int,
    stored_uuid: str,
    file_storage: FileStorage,
) -> Tuple[go.Figure, html.Div, html.Div, html.Div, html.Div, html.Div]:
    """
    Callback for projections visualization stage entry.
    It loads the data from the storage, computes and visualizes the projections.

    :param current_stage: index of the current stage
    :param stored_uuid: session uuid
    :param file_storage: file storage
    :return: figure with projections, table with projections, dropdown with projection methods
    """
    if current_stage != 1:
        return no_update

    df = pd.read_parquet(
        pa.BufferReader(file_storage.read_file(f"{stored_uuid}_smiles_merged.pq")),
    )

    fig = plot_clustered_smiles(df)
    projections_df = eos_to_ecbd_link(df)[
        ["EOS", "activity_final", "cluster_PCA", "cluster_UMAP", "cluster_UMAP3D"]
    ]
    table = table_from_df(projections_df, "projection-table")

    return fig, table


def on_smiles_dropdown_checkbox_change(
    projection_type: str,
    plot_3d_checkbox: List[str],
    stored_uuid: str,
    file_storage: FileStorage,
) -> go.Figure:
    """
    Callback for dropdown change. It loads the data from the storage and visualizes the projections.

    :param projection_type: projection method
    :param plot_3d_checkbox: 3d checkbox selection
    :param stored_uuid: session uuid
    :param file_storage: file storage
    :return: figure with projections"""

    df = pd.read_parquet(
        pa.BufferReader(file_storage.read_file(f"{stored_uuid}_smiles_merged.pq")),
    )
    return plot_clustered_smiles(
        df, projection=projection_type, plot_3d=bool(plot_3d_checkbox)
    )


def on_smiles_download_selection_button_click(
    n_clicks: int,
    selection: dict,
    stored_uuid: str,
    file_storage: FileStorage,
) -> dict:
    """
    Callback for the download selected button click. Downloads lasso/box selected datapoints
    to a csv file.

    :param n_clicks: number of clicks
    :param stored_uuid: session uuid
    :param file_storage: storage object
    """
    if not selection:
        return no_update

    datapoints = [point["pointIndex"] for point in selection["points"]]

    df = pd.read_parquet(
        pa.BufferReader(file_storage.read_file(f"{stored_uuid}_smiles_merged.pq")),
    )
    selected_subset_df = df.iloc[datapoints]
    filename = f"smiles_data_{datetime.now().strftime('%Y-%m-%d')}-selection-{selected_subset_df.shape[0]}.csv"
    return dcc.send_data_frame(selected_subset_df.to_csv, filename)


def register_callbacks(elements, file_storage: FileStorage):
    callback(
        Output("user-uuid", "data", allow_duplicate=True),
        Output("dummy-upload-activity-data", "children"),
        Input("upload-activity-data", "contents"),
        State("user-uuid", "data"),
        prevent_initial_call=True,
    )(functools.partial(on_hit_validation_upload, file_storage=file_storage))
    callback(
        Output("smiles-file-message", "children"),
        Output({"type": elements["BLOCKER"], "index": 0}, "data"),
        Output("user-uuid", "data", allow_duplicate=True),
        Output("dummy-upload-smiles-data", "children"),
        Input("dummy-upload-activity-data", "children"),
        Input("upload-activity-data", "filename"),
        Input("upload-smiles-data", "contents"),
        Input("upload-smiles-data", "filename"),
        State("user-uuid", "data"),
        prevent_initial_call=True,
    )(functools.partial(on_smiles_files_upload, file_storage=file_storage))
    callback(
        Output("smiles-projection-plot", "figure", allow_duplicate=True),
        Output("smiles-projection-table", "children"),
        Input(elements["STAGES_STORE"], "data"),
        State("user-uuid", "data"),
        prevent_initial_call=True,
    )(functools.partial(on_plot_smiles, file_storage=file_storage))
    callback(
        Output("smiles-projection-plot", "figure", allow_duplicate=True),
        Input("smiles-projection-method-selection-box", "value"),
        Input("3d-checkbox-smiles", "value"),
        State("user-uuid", "data"),
        prevent_initial_call=True,
    )(functools.partial(on_smiles_dropdown_checkbox_change, file_storage=file_storage))
    callback(
        Output("smiles-download-selection-csv", "data"),
        Input("smiles-download-selection-button", "n_clicks"),
        State("smiles-projection-plot", "selectedData"),
        State("user-uuid", "data"),
        prevent_initial_call=True,
    )(
        functools.partial(
            on_smiles_download_selection_button_click, file_storage=file_storage
        )
    )
    callback(
        Output("smiles-download-selection-button", "disabled"),
        Input("3d-checkbox-smiles", "value"),
    )(on_3d_checkbox_change)
