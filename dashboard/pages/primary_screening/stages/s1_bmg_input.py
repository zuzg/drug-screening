from dash import html, dcc

BMG_DESC = """
Lorem ipsum dolor sit amet, consectetur adipiscing elit.
In nec erat eget ante imperdiet tincidunt.
Aenean facilisis vehicula metus, nec varius elit cursus ac.
Proin quis viverra lectus. Fusce fermentum ligula mollis vulputate dignissim.
Cras tempor lacinia tincidunt. Morbi porta tellus tellus, aliquam pharetra massa tincidunt quis.
Suspendisse vitae diam et erat dapibus placerat ut eget felis.
Fusce lacinia semper quam, ac lacinia nibh porta vel.
Cras ullamcorper neque arcu, sit amet vulputate eros feugiat vitae.
"""

BMG_INPUT_STAGE = html.Div(
    id="bmg_input_stage",
    className="container",
    children=[
        html.H1(
            children=["BMG Input"],
            className="text-center",
        ),
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
