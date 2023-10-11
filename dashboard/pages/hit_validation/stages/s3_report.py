from dash import html, dcc

REPORT_STAGE = html.Div(
    id="report_stage",
    className="container",
    children=[
        html.Div(
            className="row mt-2",
            children=[
                html.Div(
                    className="col-lg-6",
                    children=[
                        html.Div(
                            className="d-flex justify-content-between",
                            children=[
                                html.Button(
                                    "Download Report",
                                    className="btn btn-primary btn-lg btn-block btn-report",
                                    id="download-report-hit-validation",
                                ),
                                dcc.Download(
                                    id="download-json-settings-hit-validation"
                                ),
                            ],
                        ),
                    ],
                ),
            ],
        ),
        html.Div(
            className="row mt-2",
            children=[
                html.Div(
                    className="col-lg-6",
                    children=[
                        html.Div(
                            className="d-flex justify-content-between",
                            children=[
                                html.Button(
                                    "Download Summary CSV",
                                    className="btn btn-primary btn-lg btn-block btn-report",
                                    id="download-csv-summary-hit-validation",
                                ),
                                dcc.Download(
                                    id="download-json-settings-hit-validation"
                                ),
                            ],
                        ),
                    ],
                ),
            ],
        ),
        html.Div(
            className="row mt-2",
            children=[
                html.Div(
                    className="col-lg-6",
                    children=[
                        html.Div(
                            className="d-flex justify-content-between",
                            children=[
                                html.Button(
                                    "Save program settings",
                                    className="btn btn-primary btn-lg btn-block btn-report",
                                    id="generate-json-button",
                                ),
                                dcc.Download(
                                    id="download-json-settings-hit-validation"
                                ),
                            ],
                        ),
                    ],
                ),
            ],
        ),
    ],
)
