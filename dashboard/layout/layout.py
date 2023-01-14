from dash import html, dcc
from .home import main_container
from .common import main_header
from .about import about_container

PAGE_Home = [
    html.Div(
        className="content",
        children=[
            main_header,
            main_container,
            dcc.Loading(
                type="default",
                className="loading-modal",
                children=[
                    html.Div(
                        id="dummy-loader",
                    )
                ],
            ),
            dcc.Store(id="data-holder", storage_type="session"),
            dcc.Store(id="controls-holder", storage_type="session"),
            dcc.Store(id="table-holder", storage_type="session"),
        ],
    )
]

PAGE_About = [
    html.Div(
        className="content",
        children=[
            main_header,
            about_container,
        ],
    )
]
