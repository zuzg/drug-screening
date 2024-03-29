import dash_bootstrap_components as dbc
from dash import dash_table, dcc, html
from dash.dash_table.Format import Format, Scheme

SUMMARY_STAGE = html.Div(
    id="summary_stage",
    className="container",
    children=[
        html.Div(
            className="mb-5 mt-4",
            children=[
                html.H5("Filter results:"),
                html.H6(
                    "The compounds in the csv report will be ones outside the range of the selected filter."
                ),
                dcc.RadioItems(
                    [],
                    value="no_filter",
                    style={"display": "flex"},
                    id="filter-radio",
                ),
            ],
        ),
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
                                    className="col-md-6 mt-1",
                                    children=[
                                        html.Div(
                                            className="row",
                                            children=[
                                                html.Div(
                                                    className="col",
                                                    children=[
                                                        html.Label("minimum value:"),
                                                        dcc.Input(
                                                            placeholder="min value",
                                                            type="number",
                                                            id="z-score-min-input",
                                                            className="stats-input",
                                                            step=0.00001,
                                                            disabled=True,
                                                            value=-3,
                                                        ),
                                                    ],
                                                ),
                                                html.Div(
                                                    className="col",
                                                    children=[
                                                        html.Label("maximum value:"),
                                                        dcc.Input(
                                                            placeholder="max value",
                                                            type="number",
                                                            id="z-score-max-input",
                                                            step=0.00001,
                                                            className="stats-input",
                                                            disabled=True,
                                                            value=3,
                                                        ),
                                                    ],
                                                ),
                                            ],
                                        )
                                    ],
                                ),
                                dcc.Loading(
                                    children=[
                                        dcc.Graph(
                                            id="z-score-plot",
                                            figure={},
                                        ),
                                    ],
                                    type="circle",
                                ),
                            ],
                        ),
                    ],
                ),
                dcc.Tab(
                    label="Activation/Inhibition",
                    children=[
                        html.Div(
                            className="my-4",
                            children=[
                                html.H5(
                                    "Activation/Inhibition range:",
                                    id="tab-feature-header",
                                ),
                                html.Div(
                                    className="col-md-6 mt-1",
                                    children=[
                                        html.Div(
                                            className="row",
                                            children=[
                                                html.Div(
                                                    className="col",
                                                    children=[
                                                        html.Label("minimum value:"),
                                                        dcc.Input(
                                                            placeholder="min value",
                                                            type="number",
                                                            id="feature-min-input",
                                                            className="stats-input",
                                                            disabled=True,
                                                        ),
                                                    ],
                                                ),
                                                html.Div(
                                                    className="col",
                                                    children=[
                                                        html.Label("maximum value:"),
                                                        dcc.Input(
                                                            placeholder="max value",
                                                            type="number",
                                                            id="feature-max-input",
                                                            className="stats-input",
                                                            disabled=True,
                                                        ),
                                                    ],
                                                ),
                                            ],
                                        )
                                    ],
                                ),
                                dcc.Loading(
                                    children=[
                                        dcc.Graph(
                                            id="feature-plot",
                                            figure={},
                                        ),
                                    ],
                                    type="circle",
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
                    className="mb-2",
                    children=[
                        html.H6(
                            children=[""],
                            className="text-center",
                            id="compounds-data-subtitle",
                        )
                    ],
                ),
                html.Div(
                    className="overflow-auto mx-2 border border-3 rounded shadow bg-body-tertiary",
                    children=[],
                    id="compounds-data-table",
                ),
            ],
        ),
    ],
)
