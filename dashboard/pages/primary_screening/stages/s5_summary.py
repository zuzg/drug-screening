from dash import dash_table, dcc, html
from dash.dash_table.Format import Format, Scheme, Trim

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
    style_table={"overflowX": "auto"},
    style_data={
        "padding-left": "10px",
        "padding-right": "10px",
        "width": "70px",
        "autosize": {"type": "fit", "resize": True},
        "overflow": "hidden",
    },
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
        html.H1(
            children=["Summary"],
            className="text-center",
        ),
        html.Div(
            className="row",
            children=[
                html.Div(
                    className="col",
                    children=[
                        dcc.Graph(
                            id="z-score-plot",
                            figure={},
                        ),
                    ],
                ),
            ],
        ),
        html.Div(
            className="row",
            children=[
                html.Div(
                    className="col",
                    children=[
                        dcc.Graph(
                            id="activation-plot",
                            figure={},
                        ),
                    ],
                ),
            ],
        ),
        html.Div(
            className="row",
            children=[
                html.Div(
                    className="col",
                    children=[
                        dcc.Graph(
                            id="inhibition-plot",
                            figure={},
                        ),
                    ],
                ),
            ],
        ),
        html.Div(
            className="row",
            children=[
                html.Div(
                    className="col my-4",
                    children=[
                        html.H2(
                            children=["Compounds Data"],
                            className="text-center",
                        ),
                        _ACT_INH_DATATABLE,
                    ],
                ),
            ],
        ),
    ],
)
