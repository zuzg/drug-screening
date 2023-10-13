import pandas as pd
from dash import dash_table, dcc, html
from dash.dash_table.Format import Format, Scheme

# Sample data for the table
data = [
    {"Column1": "Value1", "Column2": "Value2"},
    {"Column1": "Value3", "Column2": "Value4"},
]
df = pd.DataFrame(data)

# Sample options for the dropdown
dropdown_options = [
    {"label": "Option 1", "value": "option1"},
    {"label": "Option 2", "value": "option2"},
]

PROJECTION_DATATABLE = dash_table.DataTable(
    data=df.to_dict("records"),
    columns=[{"id": c, "name": c} for c in df.columns],
    id="projection-data",
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

PROJECTION_DISPLAY_STAGE = html.Div(
    [
        html.Div(
            className="row",
            children=[
                html.Div(
                    [html.H5("Compounds Data:")],
                    className="col-md-6",
                ),
                html.Div(
                    [
                        html.Div(
                            className="row",
                            children=[
                                html.Div(
                                    [html.H5("Choose the screening [TODO]:")],
                                    className="col",
                                ),
                                html.Div(
                                    [
                                        dcc.Dropdown(
                                            id="selection-box",
                                            options=dropdown_options,
                                            value=dropdown_options[0]["value"],
                                            searchable=False,
                                            clearable=False,
                                        ),
                                    ],
                                    className="col",
                                ),
                            ],
                        ),
                    ],
                    className="col-md-6",
                ),
            ],
        ),
        html.Div(
            className="row mt-3",
            children=[
                html.Div(
                    children=[
                        html.Div(
                            id="projection-table",
                        ),
                    ],
                    className="col-md-6",
                ),
                html.Div(
                    [
                        dcc.Graph(id="projection-plot", figure={}),
                    ],
                    className="col-md-6",
                ),
            ],
        ),
    ]
)
