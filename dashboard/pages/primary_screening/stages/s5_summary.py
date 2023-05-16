from dash import html

SUMMARY_STAGE = html.Div(
    id="summary_stage",
    className="container",
    children=[
        html.H1(
            children=["Summary"],
            className="text-center",
        ),
    ],
)
