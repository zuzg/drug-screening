from dash import dcc, html

from dashboard.pages.components import annotate_with_tooltip


SHOW_CONTROL_CHECKBOX_DESC = """
Select whether to show for reference how the control values will be projected relatively
to the compounds with selected settings.
"""

DOWNLOAD_SELECTION_BUTTON_DESC = """
Download the data of the compounds that are currently selected on the plot using
box or lasso selection to a csv file containing projection values and compound data.
"""

PROJECTION_DISPLAY_STAGE = html.Div(
    [
        html.Div(
            className="row",
            children=[
                html.Div(
                    [html.H5("Compounds Data:")],
                    className="col-md-6",
                ),
                html.Div(
                    [
                        html.Div(
                            className="row",
                            children=[
                                html.Div(
                                    [
                                        html.Div(
                                            id="projection-method-selection-box",
                                            children=[
                                                dcc.Dropdown(
                                                    id="projection-method-selection-box",
                                                    options=[
                                                        {
                                                            "label": "UMAP",
                                                            "value": "UMAP",
                                                        },
                                                        {
                                                            "label": "PCA",
                                                            "value": "PCA",
                                                        },
                                                    ],
                                                    value="PCA",
                                                    searchable=False,
                                                    clearable=False,
                                                    disabled=False,
                                                ),
                                            ],
                                        )
                                    ],
                                    className="col",
                                ),
                                html.Div(
                                    [
                                        html.Div(
                                            id="projection-attribute-selection-box",
                                            children=[
                                                dcc.Dropdown(
                                                    options={},
                                                    placeholder="Select an attribute",
                                                    disabled=True,
                                                ),
                                            ],
                                        )
                                    ],
                                    className="col",
                                ),
                            ],
                        ),
                    ],
                    className="col-md-6",
                ),
            ],
        ),
        html.Div(
            className="row mt-3",
            children=[
                html.Div(
                    children=[
                        dcc.Loading(
                            children=[html.Div(id="projection-table", children=[])],
                            type="circle",
                        ),
                    ],
                    className="col-md-6",
                ),
                html.Div(
                    children=[
                        dcc.Loading(
                            children=[
                                dcc.Graph(id="projection-plot", figure={}),
                            ],
                            type="circle",
                        ),
                    ],
                    className="col-md-6",
                ),
            ],
        ),
        html.Div(
            className="row",
            children=[
                html.Div(
                    children=[
                        html.Div(id="pca-info", className="row", children=[]),
                    ],
                    className="col-md-6",
                ),
                html.Div(
                    children=[
                        html.Div(
                            className="d-flex flex-row justify-content-between",
                            children=[
                                html.Span(
                                    className="d-flex flex-row align-items-center gap-3",
                                    children=[
                                        annotate_with_tooltip(
                                            html.Span(
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
                                            ),
                                            SHOW_CONTROL_CHECKBOX_DESC,
                                        ),
                                        dcc.Checklist(
                                            options=[
                                                {
                                                    "label": "  Plot 3D",
                                                    "value": "3d",
                                                }
                                            ],
                                            value=[],
                                            id="3d-checkbox",
                                        ),
                                    ],
                                ),
                                annotate_with_tooltip(
                                    html.Button(
                                        children=[
                                            "Download Selected",
                                            dcc.Download(
                                                id="projection-download-selection-csv"
                                            ),
                                        ],
                                        id="projection-download-selection-button",
                                        className="btn btn-primary",
                                    ),
                                    DOWNLOAD_SELECTION_BUTTON_DESC,
                                ),
                            ],
                        )
                    ],
                    className="col-md-6",
                ),
            ],
        ),
    ]
)
