from dash import dcc, html

SMILES_PROJECTION_DISPLAY_STAGE = html.Div(
    [
        html.Div(
            className="row",
            children=[
                html.Div(
                    [html.H5("Compounds Data")],
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
                                            id="smiles-projection-method-selection-box",
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
                            id="loading-projection-table",
                            children=[
                                html.Div(id="smiles-projection-table", children=[])
                            ],
                            type="circle",
                        ),
                    ],
                    className="col-md-6",
                ),
                html.Div(
                    children=[
                        dcc.Loading(
                            id="loading-projection-plot",
                            children=[
                                dcc.Graph(id="smiles-projection-plot", figure={}),
                            ],
                            type="circle",
                        ),
                    ],
                    className="col-md-6",
                ),
            ],
        ),
    ]
)
