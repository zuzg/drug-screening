from dash import dash_table, dcc, html

_ACT_INH_DATATABLE = dash_table.DataTable(
    id="act-inh-table",
    columns=[
        {"name": "Destination Plate Barcode", "id": "Destination Plate Barcode"},
        {"name": "Destination Well", "id": "Destination Well"},
        {"name": "Volume", "id": "Actual Volume"},
    ],
)

SUMMARY_STAGE = html.Div(
    id="summary_stage",
    className="container",
    children=[
        html.H1(
            children=["Summary"],
            className="text-center",
        ),
        html.Div(id="stage-5", children=[_ACT_INH_DATATABLE]),
    ],
)
