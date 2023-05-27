from dash import html, dcc, dash_table

_COMPOUNDS_DATATABLE = dash_table.DataTable(
    id="plates-table",
    style_table={
        "overflowX": "auto",
        "overflowY": "auto",
        # "height": "100%",
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

OUTLIERS_PURGING_STAGE = html.Div(
    id="outliers_purging_stage",
    className="container h-100 d-flex flex-column",
    children=[
        html.H1(
            children=["Outliers Purging"],
            className="text-center",
        ),
        html.Div(
            className="row flex-grow-1",
            children=[
                html.Div(
                    className="col w-50 h-100",
                    children=[
                        html.Div(
                            className="d-flex flex-column gap-3 h-100",
                            children=[
                                html.H2(
                                    children=["Plates Heatmap"],
                                    className="text-center",
                                ),
                                html.Div(
                                    className="overflow-auto mx-2 border border-3 rounded shadow bg-body-tertiary bg-primary flex-grow-1",
                                    children=[
                                        dcc.Graph(
                                            id="plates-heatmap-graph",
                                            figure={},
                                            style={"height": "100%"},
                                        ),
                                    ],
                                ),
                                html.Div(
                                    className="d-flex justify-content-center gap-2 mt-3",
                                    children=[
                                        html.Button(
                                            id="heatmap-first-btn",
                                            children=["First"],
                                            className="btn btn-secondary fixed-width-100",
                                        ),
                                        html.Button(
                                            id="heatmap-previous-btn",
                                            children=["Previous"],
                                            className="btn btn-primary fixed-width-100",
                                        ),
                                        html.Div(
                                            id="heatmap-index-display",
                                            children=["0/0"],
                                            className="text-center my-auto fixed-width-150 text-muted",
                                        ),
                                        html.Button(
                                            id="heatmap-next-btn",
                                            children=["Next"],
                                            className="btn btn-primary fixed-width-100",
                                        ),
                                        html.Button(
                                            id="heatmap-last-btn",
                                            children=["Last"],
                                            className="btn btn-secondary fixed-width-100",
                                        ),
                                    ],
                                ),
                                html.Div(
                                    className="d-flex justify-content-center gap-2 mt-3",
                                    children=[
                                        dcc.Checklist(
                                            id="heatmap-outliers-checklist",
                                            options=["Show only with outliers"],
                                            inputClassName="me-2",
                                        ),
                                    ],
                                ),
                            ],
                        ),
                    ],
                ),
                html.Div(
                    className="col d-flex flex-column gap-3 w-50 h-100",
                    children=[
                        html.Div(
                            className="d-flex flex-column gap-3 flex-grow-1 h-100",
                            children=[
                                html.H2(
                                    children=["Plates Summary"],
                                    className="text-center",
                                ),
                                html.Div(
                                    className="overflow-auto mx-2 border border-3 rounded shadow bg-body-tertiary",
                                    children=[_COMPOUNDS_DATATABLE],
                                ),
                            ],
                        ),
                        html.Div(
                            className="d-flex flex-column gap-3 mb-5",
                            children=[
                                html.H2(
                                    children=["Assay Stats"],
                                    className="text-center",
                                ),
                                html.Div(
                                    className="mx-5",
                                    children=[
                                        html.Div(
                                            className="row border-bottom",
                                            children=[
                                                html.H3(
                                                    children=["Total Plates:"],
                                                    className="col-6 text-start my-auto fs-4",
                                                ),
                                                html.H3(
                                                    id="total-plates",
                                                    children=["0"],
                                                    className="col-6 text-end pe-3 my-auto fs-4",
                                                ),
                                            ],
                                        ),
                                        html.Div(
                                            className="row border-bottom",
                                            children=[
                                                html.H3(
                                                    children=["Total Compounds:"],
                                                    className="col-6 text-start my-auto fs-4",
                                                ),
                                                html.H3(
                                                    id="total-compounds",
                                                    children=["0"],
                                                    className="col-6 text-end pe-3 my-auto fs-4",
                                                ),
                                            ],
                                        ),
                                        html.Div(
                                            className="row border-bottom",
                                            children=[
                                                html.H3(
                                                    children=["Total Outliers:"],
                                                    className="col-6 text-start my-auto fs-4",
                                                ),
                                                html.H3(
                                                    id="total-outliers",
                                                    children=["0"],
                                                    className="col-6 text-end pe-3 my-auto fs-4",
                                                ),
                                            ],
                                        ),
                                    ],
                                ),
                            ],
                        ),
                    ],
                ),
            ],
        ),
        dcc.Store(id="heatmap-start-index", data=0),
        dcc.Store(id="max-heatmap-index", data=0),
    ],
)
