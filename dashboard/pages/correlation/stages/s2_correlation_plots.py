from dash import html, dcc

from dashboard.pages.components import annotate_with_tooltip

CONCENTRATION_SLIDER_DESC = """
Choose the concentration to be used for the final compound concentration calculation that will be
visible on the plots.
"""

VOLUME_SLIDER_DESC = """
Choose the summary assay volume to be used for the compound concentration calculation that will be
visible on the plots.
"""

GRAPHS = html.Div(
    id="graphs",
    className="row",
    children=[
        html.Div(
            className="col",
            children=[
                dcc.Loading(
                    id="loading-inhibition-graph",
                    children=[
                        dcc.Graph(
                            id="inhibition-graph",
                            className="six columns",
                            style={"width": "100%"},
                        )
                    ],
                    type="circle",
                )
            ],
        ),
        html.Div(
            className="col",
            children=[
                dcc.Loading(
                    id="loading-concentration-graph",
                    children=[
                        dcc.Graph(
                            id="concentration-graph",
                            className="six columns",
                            style={"width": "100%"},
                        )
                    ],
                    type="circle",
                ),
                html.Div(
                    className="row",
                    children=[
                        html.Div(
                            className="col",
                            children=[
                                html.Span(
                                    children=[
                                        html.Label(
                                            children="Set act/inh bottom threshold",
                                            className="form-label",
                                        ),
                                        dcc.Input(
                                            id="activity-threshold-bottom-input",
                                            type="number",
                                            value=-10,
                                            min=-50,
                                            className="form-control",
                                        ),
                                    ],
                                    className="flex-grow-1",
                                ),
                            ],
                        ),
                        html.Div(
                            className="col",
                            children=[
                                html.Span(
                                    children=[
                                        html.Label(
                                            children="Set act/inh upper threshold",
                                            className="form-label",
                                        ),
                                        dcc.Input(
                                            id="activity-threshold-top-input",
                                            type="number",
                                            value=100,
                                            min=0,
                                            className="form-control",
                                        ),
                                    ],
                                    className="flex-grow-1",
                                ),
                            ],
                        ),
                    ],
                ),
            ],
        ),
    ],
)

CORRELATION_PLOTS_STAGE = html.Div(
    id="correlation_plots_stage",
    className="container",
    children=[
        html.Div(
            className="row",
            children=[
                html.Div(
                    className="col",
                    children=[
                        html.H5(
                            annotate_with_tooltip(
                                html.Span("Concentration (mM)"),
                                "Choose the concentration to be used for the summary assay volume calculation.",
                            )
                        ),
                        dcc.Slider(
                            0,
                            20,
                            value=10,
                            id="concentration-slider",
                            tooltip={
                                "placement": "bottom",
                                "always_visible": True,
                            },
                        ),
                    ],
                ),
                html.Div(
                    className="col",
                    children=[
                        html.H5(
                            annotate_with_tooltip(
                                html.Span("Summary assay volume (nL)"),
                                "Choose the summary assay volume to be used for the correlation plots.",
                            )
                        ),
                        dcc.Slider(
                            0,
                            100,
                            value=20,
                            id="volume-slider",
                            tooltip={
                                "placement": "bottom",
                                "always_visible": True,
                            },
                        ),
                    ],
                ),
            ],
        ),
        GRAPHS,
    ],
)
