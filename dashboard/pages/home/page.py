from dash import register_page, html

from dashboard.pages.builders import PageBuilder
from dashboard.pages.components import make_card_component

NAME = "Home"
register_page(path="/", name=NAME, module=__name__)

CARDS_DATA = [
    {
        "title": "Screening",
        "description": [
            "Parse and analyze data from a screening experiment, "
            "in form of raw BMG and ECHO files, with an additional EOS mapping in csv format.",
            html.Br(),
            html.Br(),
            "Facilitates Outliers Filtering, Normalization, and rich visualization of the data.",
        ],
        "icon": "fa-vials",
        "link": "/screening",
    },
    {
        "title": "Correlation Analysis",
        "description": [
            "Compare two different sets of screening data and determine correlation between them.",
            html.Br(),
            html.Br(),
            "Requires two csv files (screening process outputs) with overlapping set of compounds.",
        ],
        "icon": "fa-chart-line",
        "link": "/correlation",
    },
    {
        "title": "Hit Validation",
        "description": [
            "Determine hits from a screening experiment with compounds tested in different concentrations.",
            html.Br(),
            html.Br(),
            "Performs activity classification based on set of customizable rules on curve fit parameters.",
        ],
        "icon": "fa-magnifying-glass",
        "link": "/hit-validation",
    },
    {
        "title": "Data Projections",
        "description": [
            "Preview data projections for same set of compounds tested in different experiments.",
            html.Br(),
            html.Br(),
            "Requires a set of csv files (screening process outputs) with overlapping set of compounds.",
        ],
        "icon": "fa-circle-nodes",
        "link": "/data-projection",
    },
]

pb = PageBuilder(name=NAME)
pb.extend_layout(
    layout=html.Main(
        className="h-100 flex-grow-1 grid-1-1-1-1 gap-3 mx-auto my-5 container-xxl",
        children=[make_card_component(**card_data) for card_data in CARDS_DATA],
    )
)
layout = pb.build()
