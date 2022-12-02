"""
Contains the layout for the home page element.
"""

from dash import html, dcc

home_layout = html.Div(
    className="container",
    children=[
        html.Header(
            className="my-4",
            children=[
                html.H1(children="Drug Screening Visualizer"),
                html.Div(children="A convenient way to view your data"),
            ],
        ),
        html.Div(
            children=[
                html.Label(htmlFor="upload-data"),
                dcc.Upload(
                    id="upload-data",
                    className="border border-dark rounded p-3",
                    children=html.Div(
                        [
                            "Drag and Drop or ",
                            html.A(
                                "Select Files",
                                className="text-primary text-decoration-underline",
                            ),
                        ]
                    ),
                    multiple=True,
                ),
            ]
        ),
        html.Main(
            children=[
                html.Div(
                    html.H2("Upload sheets to view data"),
                    id="output-data-upload",
                    className="p-4 text-center",
                ),
            ],
            className="my-2 card shadow",
        ),
    ],
)