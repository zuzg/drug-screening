from dash import html, dcc

OUTLIERS_PURGING_STAGE = html.Div(
    id="outliers_purging_stage",
    className="container",
    children=[
        html.H1(
            children=["Outliers Purging"],
            className="text-center",
        ),
        html.Div(
            className="row",
            children=[
                html.Div(
                    className="col",
                    children=[
                        html.Div(
                            children=[
                                html.H2(
                                    children=["Plates Heatmap"],
                                    className="text-center",
                                ),
                                dcc.Graph(
                                    id="plates-heatmap-graph",
                                ),
                                html.Div(
                                    className="d-flex justify-content-center gap-2 mt-3",
                                    children=[
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
                                    ],
                                ),
                            ]
                        ),
                    ],
                    style={"border": "1px dashed red"},  # TODO: REMOVE
                ),
                html.Div(
                    className="col",
                    children="TEST2",
                    style={"border": "1px dashed red"},  # TODO: REMOVE
                ),
            ],
        ),
        dcc.Store(id="heatmap-start-index", data=0),
        dcc.Store(id="max-heatmap-index", data=0),
    ],
)
