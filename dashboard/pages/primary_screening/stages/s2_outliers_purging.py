from dash import html

OUTLIERS_PURGING_STAGE = html.Div(
    id="outliers_purging_stage",
    className="container",
    children=[
        html.H1(
            children=["Outliers Purging"],
            className="text-center",
        ),
    ],
)
