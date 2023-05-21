from dash import html, dcc

ECHO_INPUT_STAGE = html.Div(
    id="echo_input_stage",
    className="container",
    children=[
        html.H1(
            children=["ECHO Input"],
            className="text-center",
        ),
        html.Div(
            children=[
                dcc.Upload(
                    id="upload-echo-data",
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
            id="echo-filenames",
        ),
    ],
)
