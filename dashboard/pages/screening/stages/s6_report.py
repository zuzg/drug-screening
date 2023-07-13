import dash_bootstrap_components as dbc
from dash import html

REPORT_STAGE = html.Div(
    id="report_stage",
    className="container",
    children=[
        html.Div(
            className="my-4",
            children=[
                html.Div(
                    className="row",
                    children=[
                        html.Div(
                            className="col-lg-6",
                            children=[
                                html.Div(
                                    className="d-flex justify-content-between",
                                    children=[
                                        html.Button(
                                            "Save Results",
                                            className="btn btn-primary btn-lg btn-block btn-report",
                                            id="save-results-button",
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
                                dbc.Toast(
                                    "Results saved to echo_bmg_results.csv",
                                    id="save-results-toast",
                                    header="Saved successfully!",
                                    icon="success",
                                    dismissable=True,
                                    is_open=False,
                                    duration=3000,
                                    className="mb-3",
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
                                html.Button(
                                    "Generate Report",
                                    className="btn btn-primary btn-lg btn-block btn-report",
                                    id="generate-report-button",
                                ),
                            ],
                        ),
                    ],
                ),
            ],
        ),
    ],
)
