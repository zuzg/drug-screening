from dash import dcc, html

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
                                    [
                                        html.Div(
                                            id="projection-method-selection-box",
                                            children=[
                                                dcc.Dropdown(
                                                    options={},
                                                    placeholder="Select a method",
                                                    disabled=True,
                                                ),
                                            ],
                                        )
                                    ],
                                    className="col",
                                ),
                                html.Div(
                                    [
                                        html.Div(
                                            id="projection-attribute-selection-box",
                                            children=[
                                                dcc.Dropdown(
                                                    options={},
                                                    placeholder="Select an attribute",
                                                    disabled=True,
                                                ),
                                            ],
                                        )
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
                        dcc.Loading(
                            children=[html.Div(id="projection-table", children=[])],
                            type="circle",
                        ),
                    ],
                    className="col-md-6",
                ),
                html.Div(
                    children=[
                        dcc.Loading(
                            children=[
                                dcc.Graph(id="projection-plot", figure={}),
                            ],
                            type="circle",
                        ),
                    ],
                    className="col-md-6",
                ),
            ],
        ),
        html.Div(
            className="row",
            children=[
                html.Div(
                    children=[
                        html.Div(id="pca-info", className="row", children=[]),
                    ],
                    className="col-md-6",
                ),
                html.Div(
                    children=[html.Div(id="control-checkbox", children=[])],
                    className="col-md-6",
                ),
            ],
        ),
    ]
)
