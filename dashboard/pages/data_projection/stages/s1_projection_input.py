from dash import html, dcc

PROJECTION_DESC = """
Upload the screening data file from the screening process for data projection.
Uploading the file will start the process of caltulating and visualizing projections that can be seved as a report.
"""

FILE_INPUT_CONTAINER = html.Div(
    children=[
        html.Div(
            children=[
                html.Div(
                    children=[
                        html.H5("File Upload"),
                        html.P(PROJECTION_DESC, className="text-justify"),
                    ],
                ),
                html.Div(
                    children=[
                        dcc.Upload(
                            id="upload-projection-data",
                            accept=".csv",
                            children=html.Div(
                                [
                                    "Drag and Drop or ",
                                    html.A("Select File"),
                                ]
                            ),
                            multiple=True,
                            className="text-center",
                        ),
                    ],
                    className="upload-box",
                ),
            ],
            className="grid-2-1",
        ),
    ],
    className="mb-3",
)

PROJECTION_INPUT_STAGE = html.Div(
    id="projection_input_stage",
    className="container",
    children=[
        FILE_INPUT_CONTAINER,
        html.Div(
            id="projections-file-message",
            className="d-flex flex-row align-items-center justify-content-center",
        ),
        html.Div(
            id="projection-filenames",
        ),
    ],
)
