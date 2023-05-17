from dash import register_page, html

from dashboard.pages.builders import PageBuilder

NAME = "Home"
register_page(path="/", name=NAME, module=__name__)

pb = PageBuilder(name=NAME)
pb.extend_layout(layout=html.H1("Home"))
layout = pb.build()
