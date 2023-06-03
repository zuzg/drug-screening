from dash import html

REPORT_STAGE = html.Div(
    id="report_stage",
    className="container",
    children=[
        html.H1(
            children=["Report"],
            className="text-center",
        ),
        html.Div(
            className="my-4",
            children=[
                html.Button(
                    "Generate Report",
                    className="btn btn-primary btn-lg btn-block",
                    id="generate-report-button",
                ),
            ],
        ),
    ],
)
