import dash_bootstrap_components as dbc
from dash import dash_table, dcc, html
from dash.dash_table.Format import Format, Scheme

PRECISION = 5
ACT_INH_ZSCORE_DATATABLE = dash_table.DataTable(
    id="echo-bmg-combined",
    columns=[
        dict(id="EOS", name="ID", type="text", presentation="markdown"),
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


ACT_INH_ZSCORE_TABS = dcc.Tabs(
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
                            className="row mb-3",
                            children=[
                                html.Div(
                                    className="col-md-6 mt-1",
                                    children=[
                                        html.Div(
                                            [
                                                html.Div(
                                                    className="row",
                                                    children=[
                                                        html.Div(
                                                            className="col",
                                                            children=[
                                                                html.Label(
                                                                    "minimum value:"
                                                                ),
                                                                dcc.Input(
                                                                    placeholder="min value",
                                                                    type="number",
                                                                    id="z-score-min-input",
                                                                    className="stats-input",
                                                                    disabled=True,
                                                                ),
                                                            ],
                                                        ),
                                                        html.Div(
                                                            className="col",
                                                            children=[
                                                                html.Label(
                                                                    "maximum value:"
                                                                ),
                                                                dcc.Input(
                                                                    placeholder="max value",
                                                                    type="number",
                                                                    id="z-score-max-input",
                                                                    className="stats-input",
                                                                    disabled=True,
                                                                ),
                                                            ],
                                                        ),
                                                    ],
                                                )
                                            ],
                                        )
                                    ],
                                ),
                            ],
                        ),
                        html.Div(
                            children=[
                                dcc.Loading(
                                    id="loading-z-score-plot",
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
                            className="row mb-3",
                            children=[
                                html.Div(
                                    className="col-md-6 mt-1",
                                    children=[
                                        html.Div(
                                            [
                                                html.Div(
                                                    className="row",
                                                    children=[
                                                        html.Div(
                                                            className="col",
                                                            children=[
                                                                html.Label(
                                                                    "minimum value:"
                                                                ),
                                                                dcc.Input(
                                                                    placeholder="min value",
                                                                    type="number",
                                                                    id="activation-min-input",
                                                                    className="stats-input",
                                                                    disabled=True,
                                                                ),
                                                            ],
                                                        ),
                                                        html.Div(
                                                            className="col",
                                                            children=[
                                                                html.Label(
                                                                    "maximum value:"
                                                                ),
                                                                dcc.Input(
                                                                    placeholder="max value",
                                                                    type="number",
                                                                    id="activation-max-input",
                                                                    className="stats-input",
                                                                    disabled=True,
                                                                ),
                                                            ],
                                                        ),
                                                    ],
                                                )
                                            ],
                                        )
                                    ],
                                ),
                            ],
                        ),
                        html.Div(
                            children=[
                                dcc.Loading(
                                    id="loading-activation-plot",
                                    children=[
                                        dcc.Graph(
                                            id="activation-plot",
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
        dcc.Tab(
            label="Inhibition",
            children=[
                html.Div(
                    className="my-4",
                    children=[
                        html.H5("Inhibition range:"),
                        html.Div(
                            className="row mb-3",
                            children=[
                                html.Div(
                                    className="col-md-6 mt-1",
                                    children=[
                                        html.Div(
                                            [
                                                html.Div(
                                                    className="row",
                                                    children=[
                                                        html.Div(
                                                            className="col",
                                                            children=[
                                                                html.Label(
                                                                    "minimum value:"
                                                                ),
                                                                dcc.Input(
                                                                    placeholder="min value",
                                                                    type="number",
                                                                    id="inhibition-min-input",
                                                                    className="stats-input",
                                                                    disabled=True,
                                                                ),
                                                            ],
                                                        ),
                                                        html.Div(
                                                            className="col",
                                                            children=[
                                                                html.Label(
                                                                    "maximum value:"
                                                                ),
                                                                dcc.Input(
                                                                    placeholder="max value",
                                                                    type="number",
                                                                    id="inhibition-max-input",
                                                                    className="stats-input",
                                                                    disabled=True,
                                                                ),
                                                            ],
                                                        ),
                                                    ],
                                                )
                                            ],
                                        )
                                    ],
                                ),
                            ],
                        ),
                        html.Div(
                            children=[
                                dcc.Loading(
                                    id="loading-inhibition-plot",
                                    children=[
                                        dcc.Graph(
                                            id="inhibition-plot",
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
    ],
)


radio_values = ["Retain all", "Z-Score", "Activation", "Inhibition"]
radio_codes = ["no_filter", "z_score", "activation", "inhibition"]
radio_options = []

for i, j in zip(radio_values, radio_codes):
    radio_options.append(
        {
            "label": html.Div(
                i,
                style={
                    "display": "inline",
                    "padding-left": "0.5rem",
                    "padding-right": "2rem",
                },
            ),
            "value": j,
        }
    )

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
                    radio_options,
                    "no_filter",
                    style={"display": "flex"},
                    id="filter-radio",
                ),
            ],
        ),
        ACT_INH_ZSCORE_TABS,
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
                    children=[ACT_INH_ZSCORE_DATATABLE],
                ),
            ],
        ),
    ],
)
