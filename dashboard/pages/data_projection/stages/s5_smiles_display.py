from dash import dcc, html

CONTROLS = (
    html.Div(
        className="d-flex flex-row gap-3 align-items-center w-100",
        children=[
            html.Button(
                children=[
                    "Download Selected",
                    dcc.Download(id="smiles-download-selection-csv"),
                ],
                id="smiles-download-selection-button",
                className="btn btn-primary",
            ),
            dcc.Dropdown(
                className="min-w-150px",
                id="smiles-projection-method-selection-box",
                options=[
                    {
                        "label": "UMAP",
                        "value": "UMAP",
                    },
                    {
                        "label": "PCA",
                        "value": "PCA",
                    },
                ],
                value="PCA",
                searchable=False,
                clearable=False,
                disabled=False,
            ),
            dcc.Checklist(
                options=[
                    {
                        "label": "  Plot 3D",
                        "value": "3d",
                    }
                ],
                value=[],
                id="3d-checkbox-smiles",
            ),
        ],
    ),
)

SMILES_PROJECTION_DISPLAY_STAGE = html.Div(
    [
        html.Div(
            className="row",
            children=[
                html.Div(
                    [html.H5("Compounds Data")],
                    className="col-md-6",
                ),
                html.Div(
                    CONTROLS,
                    className="col-md-6",
                ),
            ],
        ),
        html.Div(
            className="row mt-3",
            children=[
                html.Div(
                    children=[
                        dcc.Loading(
                            id="loading-projection-table",
                            children=[
                                html.Div(id="smiles-projection-table", children=[])
                            ],
                            type="circle",
                        ),
                    ],
                    className="col-md-6",
                ),
                html.Div(
                    children=[
                        dcc.Loading(
                            id="loading-projection-plot",
                            children=[
                                dcc.Graph(id="smiles-projection-plot", figure={}),
                            ],
                            type="circle",
                        ),
                    ],
                    className="col-md-6",
                ),
            ],
        ),
    ]
)
