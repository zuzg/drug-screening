from dash import dash_table, dcc, html

from dashboard.pages.components import annotate_with_tooltip

_COMPOUNDS_DATATABLE = dash_table.DataTable(
    id="plates-table",
    style_table={
        "overflowX": "auto",
        "overflowY": "auto",
    },
    style_cell={
        "textAlign": "right",
        "minWidth": "100px",
        "width": "100px",
        "padding": "0 5px",
        "font-family": "sans-serif",
        "font-size": "12px",
    },
    style_header={
        "backgroundColor": "rgb(230, 230, 230)",
        "fontWeight": "bold",
    },
    style_data_conditional=[
        {
            "if": {"row_index": "odd"},
            "backgroundColor": "rgb(248, 248, 248)",
        },
    ],
    columns=[
        {"name": "Barcode", "id": "barcode"},
        {"name": "Z Factor", "id": "z_factor"},
        {"name": "STD Compund", "id": "std_cmpd"},
        {"name": "Mean Compund", "id": "mean_cmpd"},
        {"name": "STD Control [+]", "id": "std_pos"},
        {"name": "Mean Control [+]", "id": "mean_pos"},
        {"name": "STD Control [-]", "id": "std_neg"},
        {"name": "Mean Control [-]", "id": "mean_neg"},
    ],
)

CONTROLS = html.Div(
    className="d-flex justify-content-center gap-2 mt-3",
    children=[
        html.Button(
            id="heatmap-first-btn",
            children=[
                html.I(className="fa-solid fa-angles-left"),
            ],
            className="btn btn-primary",
        ),
        html.Button(
            id="heatmap-previous-btn",
            children=[
                html.I(className="fa-solid fa-angle-left"),
            ],
            className="btn btn-primary",
        ),
        html.Div(
            id="heatmap-index-display",
            children=["0/0"],
            className="text-center my-auto fixed-width-150 text-muted",
        ),
        html.Button(
            id="heatmap-next-btn",
            children=[
                html.I(className="fa-solid fa-angle-right"),
            ],
            className="btn btn-primary",
        ),
        html.Button(
            id="heatmap-last-btn",
            children=[
                html.I(className="fa-solid fa-angles-right"),
            ],
            className="btn btn-primary",
        ),
    ],
)

HEATMAP_SECTION = html.Div(
    className="col w-50 h-100",
    children=[
        html.Div(
            className="d-flex flex-column gap-3 h-100",
            id="plates-heatmap-container",
            children=[
                dcc.Loading(
                    children=[
                        html.Div(
                            id="plates-heatmap-subcontainer",
                            className="overflow-auto mx-2 border border-3 rounded shadow bg-body-tertiary bg-primary flex-grow-1",
                            children=[
                                dcc.Graph(
                                    id="plates-heatmap-graph",
                                    figure={},
                                    style={"height": "100%"},
                                    config={
                                        "displayModeBar": False,
                                        "scrollZoom": False,
                                    },
                                ),
                            ],
                        ),
                    ],
                    type="circle",
                ),
            ],
        ),
    ],
)

SHOW_ONLY_WITH_OUTLIERS_DESC = """
Restrict the list of heatmaps to only those that have been found to contain outliers.
"""

DATATABLE_SECTION = html.Div(
    className="col d-flex flex-column gap-3 w-50 h-100",
    children=[
        html.Div(
            className="d-flex flex-column gap-3 flex-grow-1 h-100",
            children=[
                html.Div(
                    className="overflow-auto mx-2 border border-3 rounded shadow bg-body-tertiary",
                    children=[_COMPOUNDS_DATATABLE],
                ),
            ],
        ),
    ],
)
STATS_SECTION = html.Div(
    className="d-flex flex-row justify-content-between align-items-center",
    children=[
        html.Div(
            className="d-flex flex-row gap-3 align-items-center",
            children=[
                dcc.Loading(
                    html.Button(
                        id="heatmaps-export-btn",
                        children=[
                            "Export Plates Plots",
                            dcc.Download(id="download-plates-heatmap"),
                        ],
                        className="btn btn-primary",
                    ),
                    type="circle",
                ),
                html.Span(
                    className="mx-2",
                    children=[
                        html.Span(
                            children=["Total Plates:"],
                            className="me-2",
                        ),
                        html.Span(
                            id="total-plates",
                            children=["0"],
                            className="",
                        ),
                    ],
                ),
                html.Span(
                    className="mx-2",
                    children=[
                        html.Span(
                            children=["Total Compounds:"],
                            className="me-2",
                        ),
                        html.Span(
                            id="total-compounds",
                            children=["0"],
                            className="",
                        ),
                    ],
                ),
                html.Span(
                    className="mx-2",
                    children=[
                        html.Span(
                            children=["Total Outliers:"],
                            className="me-2",
                        ),
                        html.Span(
                            id="total-outliers",
                            children=["0"],
                            className="",
                        ),
                    ],
                ),
            ],
        ),
        annotate_with_tooltip(
            html.Div(
                children=[
                    dcc.Checklist(
                        id="heatmap-outliers-checklist",
                        options=["Show only with outliers"],
                        inputClassName="me-2",
                    ),
                ],
            ),
            SHOW_ONLY_WITH_OUTLIERS_DESC,
            extra_style={"transform": "translateY(2px)"},
        ),
    ],
)

OUTLIERS_PURGING_STAGE = html.Div(
    id="outliers_purging_stage",
    className="container h-100 d-flex flex-column",
    children=[
        html.Div(
            className="row mb-2 pb-2",
            children=[
                STATS_SECTION,
            ],
        ),
        html.Div(
            className="row flex-grow-1",
            children=[
                HEATMAP_SECTION,
                DATATABLE_SECTION,
            ],
        ),
        html.Div(
            className="row",
            children=[
                CONTROLS,
            ],
        ),
        dcc.Store(id="heatmap-start-index", data=0),
        dcc.Store(id="max-heatmap-index", data=0),
    ],
)
