from dash import html, dcc

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
                dcc.Upload(
                    id="upload-echo-data",
                    accept=".csv",
                    children=html.Div(
                        [
                            "Drag and Drop or ",
                            html.A("Select Files"),
                        ]
                    ),
                    multiple=True,
                    className="text-center upload-box",
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
                dcc.Upload(
                    id="upload-eos-mapping",
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
            id="echo-filenames",
        ),
    ],
)
