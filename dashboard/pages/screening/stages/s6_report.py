from dash import html

REPORT_STAGE = html.Div(
    id="report_stage",
    className="container",
    children=[
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
        html.Div(
            id="report_callback_receiver",
        ),
    ],
)
