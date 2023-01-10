"""
Contains elements for the home page element.
"""

from dash import html, dcc

general_info_panel = html.Article(
    children=[
        html.H2(
            "General Info",
            className="border-bottom text-center",
        ),
        dcc.Loading(
            type="default",
            className="loading-modal",
            children=[html.Div(id="description-table-slot", className="mb-1 p-2")],
        ),
        html.Div(
            className="controls-container",
            children=[
                html.H3(
                    "X-axis attribute",
                    className="border-bottom text-center pt-1 fs-4",
                ),
                html.H3(
                    "Y-axis attribute",
                    className="border-bottom text-center pt-1 fs-4",
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
        dcc.Loading(
            type="circle",
            children=[html.Div(id="basic-plot-slot")],
        ),
    ],
)

projection_details_panel = html.Article(
    className="col w-50",
    children=[
        html.H2(
            "Data Projection",
            className="border-bottom text-center",
        ),
        html.Div(
            className="controls-container",
            children=[
                html.H3(
                    "Method of projection",
                    className="border-bottom text-center pt-1 fs-4",
                ),
                html.H3(
                    "Colormap attribute",
                    className="border-bottom text-center pt-1 fs-4",
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
        dcc.Loading(
            type="circle",
            children=[html.Div(id="projection-plot-slot")],
        ),
        dcc.Checklist(
            id="add-controls-checkbox",
            options=[
                {
                    "label": html.Span("Control values", className="ps-1 pe-3"),
                    "value": "add_controls",
                },
                {
                    "label": html.Img(
                        src="/assets/images/colorblind.png", className="px-1"
                    ),
                    "value": "cvd",
                },
            ],
        ),
    ],
)

preview_table_panel = html.Article(
    className="col border-end w-50",
    children=[
        html.H2(
            "Selected Data Preview",
            className="border-bottom text-center",
        ),
        html.Div(id="preview-table-slot", className="p-2"),
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
