from dash import html

FILTERED_PLATES_STATS_STAGE = html.Div(
    id="filtered_plates_stats_stage",
    className="container",
    children=[
        html.H1(
            children=["Filtered Plates Stats"],
            className="text-center",
        ),
    ],
)
