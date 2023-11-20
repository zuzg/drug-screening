from dash import dcc, html

DESC = [
    html.Span(
        """
        This process aims to facilitate for correlation analysis from the
        """
    ),
    html.Span("Confirmatory Screening", className="fw-bold"),
    html.Span(" process. Provide any two compatible files from "),
    html.A("Screening", href="/screening"),
    html.Span(" page for correlation analysis."),
]

FILE_INPUT_COMPONENT = html.Div(
    className="d-flex flex-column justify-content-evenly gap-3",
    children=[
        html.Div(
            className="flex-grow-1",
            children=[
                html.H5("First File"),
                dcc.Loading(
                    children=[
                        dcc.Upload(
                            id="upload-file-1",
                            accept=".csv",
                            children=html.Div(
                                [
                                    "Drag and Drop or ",
                                    html.A("Select", className="select-file"),
                                    " Screening file #1",
                                ]
                            ),
                            multiple=False,
                            className="text-center upload-box",
                        ),
                        html.Div(id="dummy-upload-file-1"),
                    ],
                    type="circle",
                ),
            ],
        ),
        html.Div(
            className="flex-grow-1",
            children=[
                html.H5("Second File"),
                dcc.Loading(
                    children=[
                        dcc.Upload(
                            id="upload-file-2",
                            accept=".csv",
                            children=html.Div(
                                [
                                    "Drag and Drop or ",
                                    html.A("Select", className="select-file"),
                                    " Screening file #2",
                                ]
                            ),
                            multiple=False,
                            className="text-center upload-box",
                        ),
                        html.Div(id="dummy-upload-file-2"),
                    ],
                    type="circle",
                ),
            ],
        ),
    ],
)


CORRELATION_FILES_INPUT_STAGE = html.Div(
    id="correlation_files_input_stage",
    className="container",
    children=[
        html.P(children=DESC),
        html.Div(
            className="d-flex flex-row justify-content-evenly gap-5",
            children=[
                html.Div(
                    className="flex-grow-1",
                    children=[FILE_INPUT_COMPONENT],
                ),
                html.Div(
                    className="my-auto mx-5",
                    children=[
                        html.H5("Upload Status"),
                        html.Div(
                            className="grid-2-1",
                            children=[
                                html.Span("Validation status of file #1:"),
                                html.Span("-", id="file-1-status"),
                                html.Span("Validation status of file #2:"),
                                html.Span("-", id="file-2-status"),
                                html.Span("Compatibility Check:"),
                                html.Span("-", id="compatibility-status"),
                            ],
                        ),
                    ],
                ),
            ],
        ),
    ],
)
