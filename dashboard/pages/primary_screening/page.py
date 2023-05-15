from dash import register_page, html

from dashboard.pages.builders import ProcessPageBuilder

NAME = "Primary Screening"
register_page(path="/primary-screening", name=NAME, module=__name__)

pb = ProcessPageBuilder(name=NAME)
pb.add_stage(html.H1(children=["Primary Screening-s1"]))
layout = pb.build()
