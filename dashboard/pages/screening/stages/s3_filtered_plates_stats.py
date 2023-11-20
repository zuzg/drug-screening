from dash import dcc, html

from dashboard.pages.components import annotate_with_tooltip

FILTERED_PLATES_STATS_STAGE = html.Div(
    id="filtered_plates_stats_stage",
    className="container",
    children=[
        html.Div(
            className="row",
            children=[
                html.Div(
                    className="col",
                    children=[html.H6("Filter low quality plates by Z threshold:")],
                ),
                html.Div(
                    className="col",
                    children=[
                        dcc.Slider(
                            0.0,
                            1.0,
                            value=0.5,
                            id="z-slider",
                            tooltip={
                                "placement": "bottom",
                                "always_visible": True,
                            },
                        )
                    ],
                ),
                html.Div(
                    className="col",
                    children=[
                        html.H6(id="plates-removed"),
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
                        html.Div(
                            className="row",
                            children=[
                                dcc.Loading(
                                    children=[
                                        dcc.Graph(id="control-values"),
                                    ],
                                    type="circle",
                                ),
                                html.Div(
                                    className="row",
                                    children=[
                                        html.Div(
                                            className="col",
                                            children=[
                                                dcc.Loading(
                                                    children=[
                                                        dcc.Graph(id="mean-cols-rows"),
                                                    ],
                                                    type="circle",
                                                ),
                                            ],
                                        ),
                                        html.Div(
                                            className="col",
                                            children=[
                                                dcc.Loading(
                                                    children=[
                                                        dcc.Graph(id="z-per-plate"),
                                                    ],
                                                    type="circle",
                                                ),
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
