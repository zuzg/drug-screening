from dash import html, dcc
from .home import home_layout, nav_bar, main_header

PAGE_1 = [
    home_layout,
]

PAGE_2 = [
    html.Div(
        className="content",
        children=[
            main_header,
            nav_bar,
            dcc.Store(id="data-holder", storage_type="session"),
            dcc.Store(id="controls-holder", storage_type="session"),
        ],
    )
]
