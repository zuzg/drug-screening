import base64
import functools
import io
import uuid
from datetime import datetime

import pandas as pd
import plotly.graph_objects as go
import pyarrow as pa
from dash import Input, Output, State, callback, dcc, html, no_update
from sklearn.decomposition import PCA

from dashboard.data.controls import controls_index_annotator, generate_controls
from dashboard.data.preprocess import MergedAssaysPreprocessor
from dashboard.data.utils import eos_to_ecbd_link
from dashboard.pages.components import make_file_list_component
from dashboard.storage import FileStorage
from dashboard.visualization.plots import make_projection_plot, plot_projection_2d
from dashboard.visualization.text_tables import pca_summary, table_from_df


class UMAP:
    def __init__(self, *args, **kwargs) -> None:
        pass


PROJECTION_SETUP = [
    (PCA(n_components=2), "PCA"),
    (
        UMAP(
            n_components=2,
            n_neighbors=10,
            min_dist=0.1,
        ),
        "UMAP",
    ),
]

# === STAGE 1 ===


def on_projection_files_upload(
    content: str | None,
    filenames: list[str],
    last_modified: int,
    stored_uuid: str,
    file_storage: FileStorage,
) -> tuple[html.Div, str]:
    """
    Callback for file upload. TBD

    :param content: base64 encoded file content
    :param stored_uuid: session uuid
    :param file_storage: file storage
    :return: icon indicating the status of the upload
    :return: uuid of the stored data
    """
    if content is None:
        return no_update
    if stored_uuid is None:
        stored_uuid = str(uuid.uuid4())

    projection_files = []

    for content, filename in zip(content, filenames):
        filename, extension = filename.split(".")
        if extension == "csv":
            decoded = base64.b64decode(content.split(",")[1]).decode("utf-8")
            projection_files.append((filename, io.StringIO(decoded)))

    if projection_files:
        assays_preprocessor = MergedAssaysPreprocessor()
        assays_preprocessor.combine_assays_for_projections(tuple(projection_files))
        assays_merged_df = assays_preprocessor.get_processed_compounds_df()

    saved_name = f"{stored_uuid}_assays_merged.pq"
    file_storage.save_file(saved_name, assays_merged_df.reset_index().to_parquet())

    return (
        html.Div(
            children=[
                make_file_list_component(filenames, [], 1),
            ],
        ),
        stored_uuid,
    )


# === STAGE 2 ===


def on_projections_visualization_entry(
    current_stage: int,
    stored_uuid: str,
    file_storage: FileStorage,
) -> tuple[go.Figure, html.Div, html.Div, html.Div, html.Div, html.Div]:
    """
    Callback for projections visualization stage entry.
    It loads the data from the storage, computes and visualizes the projections.

    :param current_stage: index of the current stage
    :param stored_uuid: session uuid
    :param file_storage: file storage
    :return: figure with projections, table with projections, dropdown with projection attributes,
    dropdown with projection methods, projection info, checkbox for controls
    """
    if current_stage != 1:
        return no_update

    load_name = f"{stored_uuid}_assays_merged.pq"
    merged_df = pd.read_parquet(pa.BufferReader(file_storage.read_file(load_name)))

    # take only columns with projections i.e. having % in the name
    projection_columns = [col for col in merged_df.columns if "%" in col]
    controls_df = generate_controls(projection_columns)

    assays_preprocessor = MergedAssaysPreprocessor()
    assays_preprocessor.set_compounds_df(merged_df).set_controls_df(
        controls_df
    ).set_columns_for_projection(projection_columns)

    for projector, name in PROJECTION_SETUP:
        assays_preprocessor.apply_projection(projector, name)

    projections_df = assays_preprocessor.get_processed_compounds_df()
    file_storage.save_file(
        f"{stored_uuid}_assays_projection.pq",
        projections_df.reset_index(drop=True).to_parquet(),
    )

    projection_controls_df = assays_preprocessor.annotate_controls(
        controls_index_annotator
    ).get_processed_controls_df()
    file_storage.save_file(
        f"{stored_uuid}_controls_projection.pq",
        projection_controls_df.reset_index(drop=True).to_parquet(),
    )

    dropdown_options = []
    for value in projection_columns:
        option = {"label": value, "value": value}
        dropdown_options.append(option)

    fig = plot_projection_2d(projections_df, projection_columns[0], "UMAP")
    projections_df = eos_to_ecbd_link(projections_df)
    table = table_from_df(projections_df, "projection-table")

    attribute_options = html.Div(
        children=[
            dcc.Dropdown(
                id="projection-attribute-selection-box",
                options=dropdown_options,
                value=projection_columns[0],
                searchable=False,
                clearable=False,
                disabled=False,
            ),
        ]
    )

    method_options = html.Div(
        children=[
            dcc.Dropdown(
                id="projection-method-selection-box",
                options=[
                    {"label": "UMAP", "value": "UMAP"},
                    {"label": "PCA", "value": "PCA"},
                ],
                value="UMAP",
                searchable=False,
                clearable=False,
                disabled=False,
            ),
        ]
    )

    checkbox = html.Div(
        dcc.Checklist(
            options=[
                {
                    "label": "  Show control values",
                    "value": "controls",
                }
            ],
            value=[],
            id="control-checkbox",
        )
    )

    pca = PROJECTION_SETUP[0][0]
    projection_info = pca_summary(pca, projection_columns)

    return (fig, table, attribute_options, method_options, projection_info, checkbox)


def on_dropdown_checkbox_change(
    projection_type: str,
    attribute: str,
    controls: list[str],
    stored_uuid: str,
    file_storage: FileStorage,
) -> go.Figure:
    """
    Callback for dropdown change. It loads the data from the storage and visualizes the projections.

    :param method: projection method
    :param attribute: projection attribute
    :param stored_uuid: session uuid
    :param file_storage: file storage
    :return: figure with projections"""
    compounds_df = pd.read_parquet(
        pa.BufferReader(file_storage.read_file(f"{stored_uuid}_assays_projection.pq"))
    )
    controls_df = pd.read_parquet(
        pa.BufferReader(file_storage.read_file(f"{stored_uuid}_controls_projection.pq"))
    )

    return make_projection_plot(
        compounds_df,
        controls_df,
        attribute,
        projection_type,
        controls,
    )


def on_plot_selected_data(
    relayout_data: dict,
    stored_uuid: str,
    projection_type: str,
    file_storage: FileStorage,
) -> None:
    if not relayout_data:
        return no_update

    df = pd.read_parquet(
        pa.BufferReader(file_storage.read_file(f"{stored_uuid}_assays_projection.pq")),
    )

    if "xaxis.range[0]" in relayout_data:
        x_min = relayout_data["xaxis.range[0]"]
        x_max = relayout_data["xaxis.range[1]"]
        df = df[df[f"{projection_type}_X"].between(x_min, x_max)]
    if "yaxis.range[0]" in relayout_data:
        y_min = relayout_data["yaxis.range[0]"]
        y_max = relayout_data["yaxis.range[1]"]
        df = df[df[f"{projection_type}_Y"].between(y_min, y_max)]

    return eos_to_ecbd_link(df).to_dict("records")


def on_save_projections_click(
    n_clicks: int,
    stored_uuid: str,
    file_storage: FileStorage,
) -> None:
    """
    Callback for the save projections button

    :param n_clicks: number of clicks
    :param stored_uuid: uuid of the stored data
    :param file_storage: storage object
    :return: None
    """

    filename = f"projection_data_{datetime.now().strftime('%Y-%m-%d')}.csv"

    projections_df = pd.read_parquet(
        pa.BufferReader(file_storage.read_file(f"{stored_uuid}_assays_projection.pq")),
    )

    return dcc.send_data_frame(projections_df.to_csv, filename)


def register_callbacks(elements, file_storage: FileStorage):
    callback(
        Output("projections-file-message", "children"),
        Output("user-uuid", "data", allow_duplicate=True),
        Input("upload-projection-data", "contents"),
        Input("upload-projection-data", "filename"),
        Input("upload-projection-data", "last_modified"),
        State("user-uuid", "data"),
        prevent_initial_call=True,
    )(functools.partial(on_projection_files_upload, file_storage=file_storage))
    callback(
        Output("projection-plot", "figure", allow_duplicate=True),
        Output("projection-table", "children"),
        Output("projection-attribute-selection-box", "children"),
        Output("projection-method-selection-box", "children"),
        Output("pca-info", "children"),
        Output("control-checkbox", "children"),
        Input(elements["STAGES_STORE"], "data"),
        State("user-uuid", "data"),
        prevent_initial_call=True,
    )(functools.partial(on_projections_visualization_entry, file_storage=file_storage))
    callback(
        Output("projection-plot", "figure", allow_duplicate=True),
        Input("projection-method-selection-box", "value"),
        Input("projection-attribute-selection-box", "value"),
        Input("control-checkbox", "value"),
        State("user-uuid", "data"),
        prevent_initial_call=True,
    )(functools.partial(on_dropdown_checkbox_change, file_storage=file_storage))
    callback(
        Output("download-projections-csv", "data"),
        Input("save-projections-button", "n_clicks"),
        State("user-uuid", "data"),
        prevent_initial_call=True,
    )(functools.partial(on_save_projections_click, file_storage=file_storage))
    callback(
        Output("projection-table", "data"),
        Input("projection-plot", "relayoutData"),
        State("user-uuid", "data"),
        State("projection-method-selection-box", "value"),
        prevent_initial_call=True,
    )(functools.partial(on_plot_selected_data, file_storage=file_storage))
