from dash import dcc, html

ECHO_DESC = """
ECHO files in ".csv" format should have [DETAILS] and (if there are exceptions in the file) [EXCEPTIONS] tags
in the file. A file without any tags will be treated as containing only successfully processed compounds.
Each row containing information about a compound should contain, among other things,
the barcode and position on the plate so that it is possible to link ECHO files with BMG files.
"""

EOS_DESC = "Upload file (csv) mapping plate and well to EOS."

ECHO_INPUT_STAGE = html.Div(
    id="echo_input_stage",
    className="container",
    children=[
        html.Div(
            children=[
                html.Div(
                    children=[
                        html.H5("ECHO files"),
                        html.P(ECHO_DESC, className="text-justify"),
                    ]
                ),
                dcc.Loading(
                    children=[
                        html.Div(
                            children=[
                                dcc.Upload(
                                    id="upload-echo-data",
                                    accept=".csv",
                                    children=html.Div(
                                        [
                                            "Drag and Drop or ",
                                            html.A("Select", className="select-file"),
                                            " ECHO files",
                                        ]
                                    ),
                                    multiple=True,
                                    className="text-center",
                                ),
                                html.Div(id="dummy-upload-echo-data"),
                            ],
                            className="upload-box",
                        ),
                    ],
                    type="circle",
                ),
            ],
            className="grid-2-1",
        ),
        html.Br(),
        html.Div(
            children=[
                html.Div(
                    children=[
                        html.H5("EOS mapping"),
                        html.P(EOS_DESC, className="text-justify"),
                    ]
                ),
                dcc.Loading(
                    children=[
                        dcc.Upload(
                            id="upload-eos-mapping",
                            accept=".csv",
                            children=html.Div(
                                [
                                    "Drag and Drop or ",
                                    html.A("Select", className="select-file"),
                                    " EOS mapping file",
                                ]
                            ),
                            multiple=False,
                            className="text-center upload-box",
                        ),
                        html.Div(id="dummy-upload-eos-mapping"),
                    ],
                    type="circle",
                ),
            ],
            className="grid-2-1",
        ),
        html.Div(
            children=[
                html.Div(
                    children=[
                        html.Div(
                            children=[
                                html.H5("Additional options "),
                                html.Div(
                                    children=[
                                        html.Div(
                                            className="row",
                                            children=[
                                                html.Div(
                                                    [
                                                        html.Span("Screening feature:"),
                                                        html.Div(
                                                            children=[
                                                                dcc.Dropdown(
                                                                    options=[
                                                                        {
                                                                            "label": "% ACTIVATION",
                                                                            "value": "activation",
                                                                        },
                                                                        {
                                                                            "label": "% INHIBITION",
                                                                            "value": "inhibition",
                                                                        },
                                                                    ],
                                                                    value="activation",
                                                                    id="screening-feature-dropdown",
                                                                    clearable=False,
                                                                ),
                                                            ],
                                                        ),
                                                    ],
                                                    className="col",
                                                ),
                                                html.Div(
                                                    [
                                                        html.Span(
                                                            "Activation formula:"
                                                        ),
                                                        html.Div(
                                                            children=[
                                                                dcc.Dropdown(
                                                                    options=[
                                                                        {
                                                                            "label": "((x - μn)/(μp - μn)) * 100%",
                                                                            "value": False,
                                                                        },
                                                                        {
                                                                            "label": "(x - μn)/μn * 100%",
                                                                            "value": True,
                                                                        },
                                                                    ],
                                                                    value=False,
                                                                    id="activation-formula-dropdown",
                                                                    clearable=False,
                                                                ),
                                                            ],
                                                        ),
                                                    ],
                                                    className="col",
                                                ),
                                            ],
                                        ),
                                    ],
                                ),
                            ],
                        ),
                    ],
                ),
                html.Div(),
            ],
            className="grid-2-1",
        ),
        html.Div(
            id="echo-filenames",
        ),
    ],
)
