from dash import html, dcc


FILTERED_PLATES_STATS_STAGE = html.Div(
    id="filtered_plates_stats_stage",
    className="container",
    children=[
        html.H1(
            children=["Filtered Plates Stats"],
            className="text-center",
        ),
        html.Div(
            className="row",
            children=[
                html.Div(
                    className="col",
                    children=[
                        html.Div(
                            className="row",
                            children=[
                                dcc.Graph(id="control-values"),
                                html.Div(
                                    className="row",
                                    children=[
                                        html.Div(
                                            className="col",
                                            children=[
                                                dcc.Graph(id="mean-cols-rows"),
                                            ],
                                        ),
                                        html.Div(
                                            className="col",
                                            children=[
                                                dcc.Graph(id="z-per-plate"),
                                            ],
                                        ),
                                    ],
                                ),
                            ],
                        )
                    ],
                ),
            ],
        ),
    ],
)
