from dash import html

REPORT_STAGE = html.Div(
    id="report_stage",
    className="container",
    children=[
        html.Button(
            id="download-report-projections",
            className="btn btn-primary me-3",
            children="Download Results",
        ),
    ],
)
