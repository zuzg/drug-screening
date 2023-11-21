from dash import html, dcc

from dashboard.pages.components import annotate_with_tooltip

CONCENTRATION_SLIDER_DESC = """
Choose the concentration to be used for the final compound concentration calculation that will be
visible on the Concentration plot.
"""

VOLUME_SLIDER_DESC = """
Choose the summary assay volume to be used for the compound concentration calculation that will be
visible on the Concentration plot.
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
                    children=[dcc.Graph(id="inhibition-graph")],
                    type="circle",
                )
            ],
        ),
        html.Div(
            className="col",
            children=[
                dcc.Loading(
                    id="loading-concentration-graph",
                    children=[dcc.Graph(id="concentration-graph")],
                    type="circle",
                )
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
