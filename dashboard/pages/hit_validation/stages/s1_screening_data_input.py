from dash import dcc, html

import dash_bootstrap_components as dbc
from dashboard.pages.components import annotate_with_tooltip

ACTIVY_DETERMINATION_PARAMS_DESC = """
Specify parameters used for activity classification.
Concentration bounds are used to determine the allowable range of concentrations for IC50.
Top bounds are used to determine the allowable range of TOP value of the fitted curve.
"""

PARAMS_CONTAINER = html.Div(
    children=[
        html.H5(
            children=annotate_with_tooltip(
                html.Span(
                    "Activity Determination Parameters",
                    className="pe-2",
                ),
                ACTIVY_DETERMINATION_PARAMS_DESC,
                extra_style={"transform": "translateY(10px)"},
            )
        ),
        html.Div(
            children=[
                html.Div(
                    className="d-flex flex-column flex-grow-1 w-100",
                    children=[
                        html.Span(
                            children=[
                                html.Label(
                                    children="Concentration upper bound (µM)",
                                    className="form-label",
                                ),
                                dcc.Input(
                                    id="concentration-upper-bound-input",
                                    type="number",
                                    value=10,
                                    min=0,
                                    className="form-control",
                                ),
                            ],
                            className="flex-grow-1",
                        ),
                        html.Span(
                            children=[
                                html.Label(
                                    children="Concentration lower bound (µM)",
                                    className="form-label",
                                ),
                                dcc.Input(
                                    id="concentration-lower-bound-input",
                                    type="number",
                                    value=0,
                                    min=0,
                                    className="form-control",
                                ),
                            ],
                            className="flex-grow-1",
                        ),
                    ],
                ),
                html.Div(
                    className="d-flex flex-column flex-grow-1 w-100",
                    children=[
                        html.Span(
                            children=[
                                html.Label(
                                    children="Top Upper Bound (%)",
                                    className="form-label",
                                ),
                                dcc.Input(
                                    id="top-upper-bound-input",
                                    type="number",
                                    value=80,
                                    min=0,
                                    className="form-control",
                                ),
                            ],
                            className="flex-grow-1",
                        ),
                        html.Span(
                            children=[
                                html.Label(
                                    children="Top Lower Bound (%)",
                                    className="form-label",
                                ),
                                dcc.Input(
                                    id="top-lower-bound-input",
                                    type="number",
                                    value=30,
                                    min=0,
                                    className="form-control",
                                ),
                            ],
                            className="flex-grow-1",
                        ),
                    ],
                ),
            ],
            className="d-flex flex-row justify-content-evenly gap-5",
        ),
    ],
    className="mb-3",
)

SCREENING_DESC = """
Upload the screening data file from the screening process for hit determination.
Uploading the file will start the hit determination process.
"""

FILE_INPUT_CONTAINER = html.Div(
    children=[
        html.H5("File Upload"),
        html.Div(
            children=[
                html.Div(
                    children=[
                        html.P(SCREENING_DESC, className="text-justify"),
                        html.P(
                            children=[
                                html.Span("Note: ", className="fw-bold"),
                                "after changing the parameters, the file needs to be re-uploaded.",
                            ]
                        ),
                    ],
                ),
                html.Div(
                    children=[
                        dcc.Loading(
                            children=[
                                html.Div(
                                    children=[
                                        dcc.Upload(
                                            id="upload-screening-data",
                                            accept=".csv",
                                            children=html.Div(
                                                [
                                                    "Drag and Drop or ",
                                                    html.A(
                                                        "Select",
                                                        className="select-file",
                                                    ),
                                                    " Hit Validation input file",
                                                ]
                                            ),
                                            multiple=False,
                                            className="text-center",
                                        ),
                                        html.Div(id="dummy-upload-screening-data"),
                                    ],
                                    className="upload-box m-1",
                                ),
                            ],
                            type="circle",
                        ),
                        dcc.Loading(
                            children=[
                                dcc.Upload(
                                    id="upload-settings-hit-validation",
                                    accept=".json",
                                    children=html.Div(
                                        [
                                            "Drag and Drop or ",
                                            html.A("Select", className="select-file"),
                                            " Settings for hit validation",
                                        ]
                                    ),
                                    multiple=False,
                                    className="text-center upload-box m-1",
                                ),
                                html.Div(
                                    id="dummy-upload-settings-hit-validation",
                                    className="p-1",
                                ),
                            ],
                            type="circle",
                        ),
                        dbc.Alert(
                            html.Div(id="alert-upload-settings-hit-validation-text"),
                            id="alert-upload-settings-hit-validation",
                            dismissable=True,
                            is_open=False,
                            duration=4000,
                            className="m-1",
                        ),
                    ],
                ),
            ],
            className="grid-1-1",
        ),
    ],
    className="mb-3",
)

SCREENING_INPUT_STAGE = html.Div(
    id="screening_input_stage",
    className="container",
    children=[
        PARAMS_CONTAINER,
        html.Span(
            className="d-flex flex-row justify-content-between gap-5",
            children=[
                html.Div(
                    id="concentration-parameters-message",
                    className="d-flex flex-row align-items-center justify-content-center",
                ),
                html.Div(
                    id="top-parameters-message",
                    className="d-flex flex-row align-items-center justify-content-center",
                ),
            ],
        ),
        html.Hr(),
        FILE_INPUT_CONTAINER,
        html.Div(
            id="screening-file-message",
            className="d-flex flex-row align-items-center justify-content-center",
        ),
    ],
)
