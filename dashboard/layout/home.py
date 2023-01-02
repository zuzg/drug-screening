"""
Contains the layout for the home page element.
"""

from dash import html, dcc

main_header = html.Header(
    className="p-3 mb-3 text-bg-dark",
    children=[
        html.Div(
            className="container-xxl",
            children=[
                html.Div(
                    className="d-flex flex-wrap align-items-center justify-content-between",
                    children=[
                        html.H1("Drug Screening Dashboard"),
                        html.Div(
                            className="text-end",
                            children=[
                                dcc.Upload(
                                    "Upload",
                                    className="btn btn-warning",
                                    id="upload-data",
                                    multiple=True,
                                    accept=".xls, .xlsx",
                                )
                            ],
                        ),
                    ],
                )
            ],
        )
    ],
)

general_info_panel = html.Article(
    children=[
        html.H2(
            "General Info",
            className="border-bottom",
            style={"textAlign": "center"},
        ),
        dcc.Loading(
            type="default",
            className="loading-modal",
            children=[html.Div(id="description-table-slot", className="mb-1")],
        ),
        html.Div(
            className="controls-container",
            children=[
                html.H3(
                    "X-axis attribute",
                    className="border-bottom",
                    style={
                        "fontSize": 25,
                        "textAlign": "center",
                        "padding-top": 10,
                    },
                ),
                html.H3(
                    "Y-axis attribute",
                    className="border-bottom",
                    style={
                        "fontSize": 25,
                        "textAlign": "center",
                        "padding-top": 10,
                    },
                ),
                dcc.Dropdown(
                    placeholder="Select X-axis attribute",
                    id="x-axis-dropdown",
                    clearable=False,
                ),
                dcc.Dropdown(
                    placeholder="Select Y-axis attribute",
                    id="y-axis-dropdown",
                    clearable=False,
                ),
            ],
        ),
        html.Div(id="basic-plot-slot"),
    ],
)

projection_details_panel = html.Article(
    className="col w-50",
    children=[
        html.H2(
            "Data Projection",
            className="border-bottom",
            style={"textAlign": "center"},
        ),
        html.Div(
            className="controls-container",
            children=[
                html.H3(
                    "Method of projection",
                    className="border-bottom",
                    style={
                        "fontSize": 25,
                        "textAlign": "center",
                        "padding-top": 10,
                    },
                ),
                html.H3(
                    "Colormap attribute",
                    className="border-bottom",
                    style={
                        "fontSize": 25,
                        "textAlign": "center",
                        "padding-top": 10,
                    },
                ),
                dcc.Dropdown(
                    id="projection-type-dropdown",
                    options=["UMAP", "PCA", "TSNE"],
                    value="UMAP",
                    clearable=False,
                ),
                dcc.Dropdown(
                    placeholder="Select colormap attribute",
                    id="colormap-attribute-dropdown",
                    clearable=False,
                ),
            ],
        ),
        html.Div(
            dcc.Checklist(
                id="add-controls-checkbox", options={True: " Add control values"}
            )
        ),
        html.Div(id="projection-plot-slot"),
    ],
)

preview_table_panel = html.Article(
    className="col border-end w-50",
    children=[
        html.H2(
            "Selected Data Preview",
            className="border-bottom",
            style={"textAlign": "center"},
        ),
        html.Div(id="preview-table-slot"),
    ],
)

main_container = html.Main(
    className="container-xl flex-grow-1",
    children=[
        html.Div(
            className="row",
            children=[
                preview_table_panel,
                projection_details_panel,
                general_info_panel,
            ],
        ),
    ],
)

home_layout = html.Div(
    className="content",
    children=[
        main_header,
        main_container,
        dcc.Store(id="data-holder", storage_type="session"),
        dcc.Store(id="controls-holder", storage_type="session"),
    ],
)
