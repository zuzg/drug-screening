"""
Contains common elements for the pages.
"""

from dash import html, dcc

nav_bar = html.Div(
    children=[
        html.Div(
            children=[
                html.Button(
                    "Home",
                    id="home-button",
                    className="nav-button px-1 text-white text-bg-dark border-0",
                    n_clicks=0,
                ),
                html.Button(
                    "About",
                    id="about-button",
                    className="nav-button px-4 text-white text-bg-dark border-0",
                    n_clicks=0,
                ),
            ]
        ),
    ],
    className="nav-bar",
)

main_header = html.Header(
    className="p-3 mb-3 text-bg-dark",
    children=[
        html.Div(
            className="container-xxl",
            children=[
                html.Div(
                    className="d-flex flex-wrap align-items-center justify-content-between",
                    children=[
                        html.H1("Drug Screening Dashboard"),
                        html.Div(
                            className="d-flex flex-wrap align-items-center justify-content-between m-1 text-end",
                            children=[
                                nav_bar,
                                dcc.Upload(
                                    "Upload",
                                    className="btn btn-warning",
                                    id="upload-data",
                                    multiple=True,
                                    accept=".xls, .xlsx",
                                ),
                            ],
                        ),
                    ],
                ),
            ],
        )
    ],
)
