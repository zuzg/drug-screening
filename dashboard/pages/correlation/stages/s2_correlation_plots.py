from dash import html, dcc

GRAPHS = html.Div(
    id="graphs",
    className="d-flex flex-row",
    children=[
        dcc.Graph(
            id="inhibition-graph", className="six columns", style={"width": "50%"}
        ),
        dcc.Graph(
            id="concentration-graph", className="six columns", style={"width": "50%"}
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
                        html.H5("Concentration (mM)"),
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
                        html.H5("Summary assay volume (nL)"),
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
