from dash import html, dcc

REPORT_STAGE = html.Div(
    id="report_stage",
    className="container",
    children=[
        html.Button(
            id="download-report",
            className="btn btn-primary",
            children="Download report",
        ),
    ],
)
