import dash_bootstrap_components as dbc
from dash import dcc, html

REPORT_STAGE = html.Div(
    id="report_stage",
    className="container",
    children=[
        html.Div(
            className="my-4",
            children=[
                html.Div(className="row", children=[html.H5("Save results:")]),
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
                                            "Save screening results as CSV",
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
                            className="col-lg-6",
                            children=[
                                html.Div(
                                    className="d-flex justify-content-between",
                                    children=[
                                        html.Button(
                                            "Save exceptions as CSV",
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
                            className="col-lg-6",
                            children=[
                                html.Div(
                                    className="d-flex justify-content-between",
                                    children=[
                                        html.Button(
                                            "Generate HTML report",
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
                                            id="download-json-settings-screening"
                                        ),
                                    ],
                                ),
                            ],
                        ),
                    ],
                ),
                html.Div(
                    id="report_callback_receiver",
                ),
            ],
        ),
    ],
)
