from dash import html, dcc

FILE_INPUT_CONTAINER = html.Div(
    children=[
        html.Div(
            children=[
                html.Div(
                    children=[
                        html.H5("Active SMILES"),
                        html.P(
                            "Upload file with results from IC50 fitting (with column acitivity_final)",
                            className="text-justify",
                        ),
                    ],
                ),
                html.Div(
                    children=[
                        dcc.Upload(
                            id="upload-activity-data",
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
            className="grid-2-1",
        ),
        html.Br(),
        html.Div(
            children=[
                html.Div(
                    children=[
                        html.H5("New SMILES Upload"),
                        html.P(
                            "Upload file with untested SMILES to check structural similarity",
                            className="text-justify",
                        ),
                    ],
                ),
                html.Div(
                    children=[
                        dcc.Upload(
                            id="upload-smiles-data",
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
            className="grid-2-1",
        ),
    ],
    className="mb-3",
)

SMILES_INPUT_STAGE = html.Div(
    id="smiles_input_stage",
    className="container",
    children=[
        FILE_INPUT_CONTAINER,
        html.Div(
            id="smiles-file-message",
        ),
    ],
)
