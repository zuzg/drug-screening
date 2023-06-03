from dash import html, dcc

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
                dcc.Upload(
                    id="upload-bmg-data",
                    accept=".txt",
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
        html.Div(
            id="bmg-filenames",
        ),
    ],
)
