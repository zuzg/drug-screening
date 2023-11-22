from dash import dcc, html

FILE_PARAMS = [
    {
        "id": "upload-activity-data",
        "title": "Active SMILES",
        "msg": "Upload a csv file with results from IC50 fitting (with column acitivity_final)",
        "upload_text": [
            "Drag and Drop or ",
            html.A("Select", className="select-file"),
            " Hit Validation file",
        ],
    },
    {
        "id": "upload-smiles-data",
        "title": "New SMILES",
        "msg": "Upload a csv file with untested SMILES to check structural similarity (must contain 'EOS' and 'smiles' columns)",
        "upload_text": [
            "Drag and Drop or ",
            html.A("Select", className="select-file"),
            " SMILES file",
        ],
    },
]


FILE_INPUT_CONTAINER_CHILDREN = [
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
                            param["upload_text"],
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
]


FILE_INPUT_CONTAINER = html.Div(
    children=[
        FILE_INPUT_CONTAINER_CHILDREN[0],
        html.Br(),
        FILE_INPUT_CONTAINER_CHILDREN[1],
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
