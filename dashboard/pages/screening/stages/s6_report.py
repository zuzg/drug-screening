import dash_bootstrap_components as dbc
from dash import dcc, html

from dashboard.visualization.text_tables import make_download_button_text

REPORT_STAGE = html.Div(
    id="report_stage",
    className="container",
    children=[
        html.Div(
            className="my-4",
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
                                        html.Button(
                                            make_download_button_text(
                                                "Save screening results as CSV"
                                            ),
                                            className="btn btn-primary btn-lg btn-block btn-report",
                                            id="save-results-button",
                                        ),
                                        dcc.Download(id="download-echo-bmg-combined"),
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
                                            make_download_button_text(
                                                "Save exceptions as CSV"
                                            ),
                                            className="btn btn-primary btn-lg btn-block btn-report",
                                            id="save-exceptions-button",
                                        ),
                                        dcc.Download(id="download-exceptions-csv"),
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
                                            make_download_button_text(
                                                "Generate HTML report"
                                            ),
                                            className="btn btn-primary btn-lg btn-block btn-report",
                                            id="generate-report-button",
                                        ),
                                        dcc.Download(id="download-html-raport"),
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
                                            make_download_button_text(
                                                "Save program settings"
                                            ),
                                            className="btn btn-primary btn-lg btn-block btn-report",
                                            id="generate-json-button",
                                        ),
                                        dcc.Download(
                                            id="download-json-settings-screening"
                                        ),
                                    ],
                                ),
                            ],
                        ),
                    ],
                ),
            ],
        ),
    ],
)
