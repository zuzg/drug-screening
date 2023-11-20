from dash import html, register_page

from dashboard.pages.builders import PageBuilder
from dashboard.pages.components import make_card_component

NAME = "Data Projections"
register_page(path="/data-projection", name=NAME, module=__name__)

CARDS_DATA = [
    {
        "title": "Screening Data Projections",
        "description": [
            "BLABLA Screening Data Projections.",
            html.Br(),
            html.Br(),
            "Requires a set of csv files (screening process outputs) with overlapping set of compounds.",
        ],
        "icon": "fa-magnifying-glass",
        "link": "/data-projection-screening",
    },
    {
        "title": "SMILES Data Projections",
        "description": [
            "BLABLA SMILES Data Projections.",
            html.Br(),
            html.Br(),
            "Requires SMILES Data Projections TODO.",
        ],
        "icon": "fa-circle-nodes",
        "link": "/data-projection-smiles",
    },
]

children = [html.Div(), None, None, html.Div()]
children[1:3] = [make_card_component(**card_data) for card_data in CARDS_DATA]

pb = PageBuilder(name=NAME)
pb.extend_layout(
    layout=html.Main(
        className="h-100 flex-grow-1 grid-1-1-1-1 gap-3 mx-auto my-5 container-xxl",
        children=children,
    )
)
layout = pb.build()
