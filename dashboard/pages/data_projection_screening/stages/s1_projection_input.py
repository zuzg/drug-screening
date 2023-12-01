from dash import dcc, html

PROJECTION_DESC = """
Upload at least 3 result files from the screening process for data projection.
Facilitates  projection of the data to a 2D/3D space and visualization of the results.
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
                dcc.Loading(
                    children=[
                        html.Div(
                            children=[
                                dcc.Upload(
                                    id="upload-projection-data",
                                    accept=".csv",
                                    children=html.Div(
                                        [
                                            "Drag and Drop or ",
                                            html.A("Select", className="select-file"),
                                            " Screening files",
                                        ]
                                    ),
                                    multiple=True,
                                    className="text-center",
                                ),
                                html.Div(id="dummy-upload-projection-data"),
                            ],
                            className="upload-box",
                        ),
                    ],
                    type="circle",
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
        ),
    ],
)
