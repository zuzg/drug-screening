import dash_bootstrap_components as dbc
from dash import dash_table, dcc, html
from dash.dash_table.Format import Format, Scheme

PRECISION = 5
_ACT_INH_DATATABLE = dash_table.DataTable(
    id="echo-bmg-combined",
    columns=[
        dict(id="CMPD ID", name="ID"),
        dict(id="Destination Plate Barcode", name="Plate Barcode"),
        dict(id="Destination Well", name="Well"),
        dict(
            id="% ACTIVATION",
            name=" % ACTIVATION",
            type="numeric",
            format=Format(precision=PRECISION, scheme=Scheme.fixed),
        ),
        dict(
            id="% INHIBITION",
            name=" % INHIBITION",
            type="numeric",
            format=Format(precision=PRECISION, scheme=Scheme.fixed),
        ),
        dict(
            id="Z-SCORE",
            name=" Z-SCORE",
            type="numeric",
            format=Format(precision=PRECISION, scheme=Scheme.fixed),
        ),
    ],
    style_table={"overflowX": "auto", "overflowY": "auto"},
    style_data={
        "padding-left": "10px",
        "padding-right": "10px",
        "width": "70px",
        "autosize": {"type": "fit", "resize": True},
        "overflow": "hidden",
    },
    style_cell={
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
    filter_action="native",
    filter_options={"case": "insensitive"},
    sort_action="native",
    column_selectable=False,
    page_size=15,
)

SUMMARY_STAGE = html.Div(
    id="summary_stage",
    className="container",
    children=[
        dcc.Tabs(
            id="summary-tabs",
            children=[
                dcc.Tab(
                    label="Z-Score",
                    children=[
                        html.Div(
                            className="my-4",
                            children=[
                                html.H5("Z-Score range:"),
                                html.Div(
                                    className="row",
                                    children=[
                                        html.Div(
                                            className="col mb-4",
                                            children=[
                                                dcc.RangeSlider(
                                                    -10,
                                                    10,
                                                    value=[-3, 3],
                                                    tooltip={
                                                        "placement": "bottom",
                                                        "always_visible": True,
                                                    },
                                                    allowCross=False,
                                                    id="z-score-slider",
                                                )
                                            ],
                                            style={"width": "750px"},
                                        ),
                                        html.Div(
                                            className="col",
                                            children=[
                                                dbc.Button("Apply", id="z-score-button")
                                            ],
                                        ),
                                    ],
                                ),
                                dcc.Graph(
                                    id="z-score-plot",
                                    figure={},
                                ),
                            ],
                        ),
                    ],
                ),
                dcc.Tab(
                    label="Activation",
                    children=[
                        html.Div(
                            className="my-4",
                            children=[
                                html.H5("Activation range:"),
                                html.Div(
                                    className="row",
                                    children=[
                                        html.Div(
                                            className="col mb-4",
                                            children=[
                                                dcc.RangeSlider(
                                                    0,
                                                    100,
                                                    value=[0, 100],
                                                    tooltip={
                                                        "placement": "bottom",
                                                        "always_visible": True,
                                                    },
                                                    allowCross=False,
                                                    id="activation-slider",
                                                )
                                            ],
                                            style={"width": "750px"},
                                        ),
                                        html.Div(
                                            className="col",
                                            children=[
                                                dbc.Button(
                                                    "Apply", id="activation-button"
                                                )
                                            ],
                                        ),
                                    ],
                                ),
                                dcc.Graph(
                                    id="activation-plot",
                                    figure={},
                                ),
                            ],
                        ),
                    ],
                ),
                dcc.Tab(
                    label="Inhibition",
                    children=[
                        html.Div(
                            className="my-4",
                            children=[
                                html.H5("Inhibition range:"),
                                html.Div(
                                    className="row",
                                    children=[
                                        html.Div(
                                            className="col mb-4",
                                            children=[
                                                dcc.RangeSlider(
                                                    0,
                                                    100,
                                                    value=[0, 100],
                                                    tooltip={
                                                        "placement": "bottom",
                                                        "always_visible": True,
                                                    },
                                                    allowCross=False,
                                                    id="inhibition-slider",
                                                )
                                            ],
                                            style={"width": "750px"},
                                        ),
                                        html.Div(
                                            className="col",
                                            children=[
                                                dbc.Button(
                                                    "Apply", id="inhibition-button"
                                                )
                                            ],
                                        ),
                                    ],
                                ),
                                dcc.Graph(
                                    id="inhibition-plot",
                                    figure={},
                                ),
                            ],
                        ),
                    ],
                ),
            ],
        ),
        html.Div(
            className="my-4",
            children=[
                html.Div(
                    className="mb-2",
                    children=[
                        html.H2(
                            children=["Compounds Data"],
                            className="text-center",
                        ),
                    ],
                ),
                html.Div(
                    className="overflow-auto mx-2 border border-3 rounded shadow bg-body-tertiary",
                    children=[_ACT_INH_DATATABLE],
                ),
            ],
        ),
    ],
)
