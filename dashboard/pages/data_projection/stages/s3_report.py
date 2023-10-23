from dash import dcc, html

REPORT_STAGE = html.Div(
    id="report_stage",
    className="container",
    children=[
        html.Div(
            className="d-flex justify-content-between",
            children=[
                html.Button(
                    "Save projection data as CSV",
                    className="btn btn-primary btn-lg btn-block btn-report",
                    id="save-projections-button",
                ),
                dcc.Download(id="download-projections-csv"),
            ],
        ),
    ],
)
