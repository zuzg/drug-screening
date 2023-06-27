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
    id="correlation_plots_stage", className="container", children=[GRAPHS]
)
