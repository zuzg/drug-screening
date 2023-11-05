from dash import html, dcc


FILE_PARAMS = [
    {
        "id": "upload-activity-data",
        "title": "Active SMILES",
        "msg": "Upload file with results from IC50 fitting (with column acitivity_final)",
    },
    {
        "id": "upload-smiles-data",
        "title": "New SMILES",
        "msg": "Upload file with untested SMILES to check structural similarity",
    },
]


FILE_INPUT_CONTAINER = html.Div(
    children=[
        html.Div(
            children=[
                html.Div(
                    children=[
                        html.H5(param["title"]),
                        html.P(
                            param["msg"],
                            className="text-justify",
                        ),
                    ],
                ),
                html.Div(
                    children=[
                        dcc.Upload(
                            id=param["id"],
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
                html.Br(),
            ],
            className="grid-2-1",
        )
        for param in FILE_PARAMS
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
