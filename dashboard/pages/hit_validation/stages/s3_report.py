from dash import dcc, html

from dashboard.visualization.text_tables import make_download_button_text

REPORT_STAGE = html.Div(
    id="report_stage",
    className="container",
    children=[
        html.Div(
            className="row mt-2",
            children=[
                html.Div(
                    className="col",
                    children=[
                        html.Div(
                            className="d-flex justify-content-center",
                            children=[
                                dcc.Loading(
                                    children=[
                                        html.Button(
                                            make_download_button_text(
                                                "Download Report XLSX"
                                            ),
                                            className="btn btn-primary btn-lg btn-block btn-report",
                                            id="download-report-hit-validation-button",
                                        ),
                                        dcc.Download(
                                            id="download-report-hit-validation"
                                        ),
                                    ],
                                    type="circle",
                                )
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
                    className="col",
                    children=[
                        html.Div(
                            className="d-flex justify-content-center",
                            children=[
                                html.Button(
                                    make_download_button_text("Download Report CSV"),
                                    className="btn btn-primary btn-lg btn-block btn-report",
                                    id="download-csv-summary-hit-validation-button",
                                ),
                                dcc.Download(id="download-csv-summary-hit-validation"),
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
                    className="col",
                    children=[
                        html.Div(
                            className="d-flex justify-content-center",
                            children=[
                                html.Button(
                                    make_download_button_text("Save program settings"),
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
