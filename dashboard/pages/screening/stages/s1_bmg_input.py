from dash import dcc, html

BMG_DESC = """BMG files in ".txt" format should be in the form of two columns,
where the first column contains the well unique to the plate, e.g. A02, M13, P24, etc.
The second column is the value for a given compound obtained in a given experiment.
The name of each file is also the plate identifier.
"""

BMG_INPUT_STAGE = html.Div(
    id="bmg_input_stage",
    className="container",
    children=[
        html.Div(
            children=[
                html.P(BMG_DESC, className="text-justify"),
                html.Div(
                    children=[
                        dcc.Loading(
                            children=[
                                dcc.Upload(
                                    id="upload-bmg-data",
                                    accept=".txt",
                                    children=html.Div(
                                        [
                                            "Drag and Drop or ",
                                            html.A("Select", className="select-file"),
                                            " BMG files",
                                        ]
                                    ),
                                    multiple=True,
                                    className="text-center upload-box",
                                ),
                                html.Div(
                                    id="dummy-upload-bmg-data",
                                    className="p-1",
                                ),
                            ],
                            type="circle",
                        ),
                        dcc.Loading(
                            children=[
                                dcc.Upload(
                                    id="upload-settings-screening",
                                    accept=".json",
                                    children=html.Div(
                                        [
                                            "Drag and Drop or ",
                                            html.A("Select", className="select-file"),
                                            " Settings for screening",
                                        ]
                                    ),
                                    multiple=False,
                                    className="text-center upload-box",
                                ),
                            ],
                            type="circle",
                        ),
                    ]
                ),
            ],
            className="grid-2-1",
        ),
        html.Div(
            id="bmg-filenames",
        ),
    ],
)
