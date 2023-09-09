from dash import html, dcc

SCREENING_DESC = """Upload the screening data file from the screening process."""

SCREENING_INPUT_STAGE = html.Div(
    id="screening_input_stage",
    className="container",
    children=[
        html.Div(
            children=[
                html.P(SCREENING_DESC, className="text-justify"),
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
                    className="text-center upload-box",
                ),
            ],
            className="grid-2-1",
        ),
        html.Div(
            id="screening-file-message",
        ),
    ],
)
