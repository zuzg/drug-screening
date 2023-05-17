from dash import html

ECHO_INPUT_STAGE = html.Div(
    id="echo_input_stage",
    className="container",
    children=[
        html.H1(
            children=["ECHO Input"],
            className="text-center",
        ),
    ],
)
