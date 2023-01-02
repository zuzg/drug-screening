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
    className="col border-end w-50",
    children=[
        html.H2("General Info", className="border-bottom"),
        dcc.Loading(
            type="default",
            className="loading-modal",
            children=[html.Div(id="description-table-slot", className="mb-1")],
        ),
        html.Div(
            className="controls-container",
            children=[
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
        html.H2("Data Projection", className="border-bottom"),
        html.Div(
            className="controls-container",
            children=[
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
        dcc.Checklist(
                id="add-controls-checkbox", 
                # style={'paddingLeft': 10},
                options=[
                    {
                        "label": "   Control values",
                        # html.Div(
                        #     "Control values" ,style={'paddingLeft': 5}
                        # ),
                        "value": "add_controls",
                    },
                    {
                        "label": html.Img(src="/assets/images/colorblind.png", style={'paddingLeft': 5}),
                        "value": "cvd",
                    }
                ]
        ),
        html.Div(id="projection-plot-slot"),
    ],
)

preview_table_panel = html.Article(
    className="mt-3",
    children=[
        html.H2("Selected Data Preview", className="border-bottom"),
        html.Div(id="preview-table-slot"),
    ],
)

main_container = html.Main(
    className="container-xl flex-grow-1",
    children=[
        html.Div(
            className="row",
            children=[
                general_info_panel,
                projection_details_panel,
                preview_table_panel,
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
