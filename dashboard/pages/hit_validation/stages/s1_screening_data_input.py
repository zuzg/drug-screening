from dash import html, dcc

PARAMS_CONTAINER = html.Div(
    children=[
        html.H5(
            children="Activity Determination Parameters",
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
                        dcc.Upload(
                            id="upload-screening-data",
                            accept=".csv",
                            children=html.Div(
                                [
                                    "Drag and Drop or ",
                                    html.A("Select File"),
                                ]
                            ),
                            multiple=False,
                            className="text-center",
                        ),
                    ],
                    className="upload-box",
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
